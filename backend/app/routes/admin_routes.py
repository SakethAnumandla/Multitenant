from flask import Blueprint, request, jsonify
from app.database import db
from app.models.admin import Admin
from app.models.tenant import Tenant
from app.utils.auth import authenticate_admin, hash_password
from app.utils.jwt_manager import create_access_token, token_required
from app.utils.validators import (
    validate_email_format, 
    validate_password_strength,
    validate_phone_number,
    validate_slug,
    generate_slug_from_name,
    validate_gst_number,
    validate_pan_number
)

# Create Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        
        # Authenticate admin
        admin = authenticate_admin(email, password)
        
        if not admin:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        token = create_access_token(
            user_id=admin.id,
            user_type='admin',
            email=admin.email,
            role='super_admin'
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'admin': admin.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/tenants', methods=['GET'])
@token_required(user_types=['admin'])
def get_all_tenants():
    """Get all tenants - Admin only"""
    try:
        # Query parameters for pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query tenants with pagination
        tenants_pagination = Tenant.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        tenants_list = [tenant.to_dict() for tenant in tenants_pagination.items]
        
        return jsonify({
            'tenants': tenants_list,
            'total': tenants_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': tenants_pagination.pages
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/tenants/<int:tenant_id>', methods=['GET'])
@token_required(user_types=['admin'])
def get_tenant_by_id(tenant_id):
    """Get specific tenant by ID - Admin only"""
    try:
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        return jsonify({'tenant': tenant.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/tenants', methods=['POST'])
@token_required(user_types=['admin'])
def create_tenant():
    """Create new tenant - Admin only"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'admin_name', 'admin_email', 'admin_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email formats
        is_valid, result = validate_email_format(data['email'])
        if not is_valid:
            return jsonify({'error': f'Invalid tenant email: {result}'}), 400
        
        is_valid, result = validate_email_format(data['admin_email'])
        if not is_valid:
            return jsonify({'error': f'Invalid admin email: {result}'}), 400
        
        # Validate password strength
        is_valid, message = validate_password_strength(data['admin_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Validate phone if provided
        if data.get('phone'):
            is_valid, result = validate_phone_number(data['phone'])
            if not is_valid:
                return jsonify({'error': result}), 400
            data['phone'] = result
        
        # Generate or validate slug
        if data.get('slug'):
            is_valid, message = validate_slug(data['slug'])
            if not is_valid:
                return jsonify({'error': message}), 400
            slug = data['slug']
        else:
            slug = generate_slug_from_name(data['name'])
        
        # Check if slug already exists
        if Tenant.query.filter_by(slug=slug).first():
            return jsonify({'error': 'Slug already exists'}), 400
        
        # Check if emails already exist
        if Tenant.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Tenant email already exists'}), 400
        
        if Tenant.query.filter_by(admin_email=data['admin_email']).first():
            return jsonify({'error': 'Admin email already exists'}), 400
        
        # Validate metadata (GST, PAN, etc.)
        metadata = data.get('metadata', {})
        
        if metadata.get('gst'):
            is_valid, result = validate_gst_number(metadata['gst'])
            if not is_valid:
                return jsonify({'error': result}), 400
            metadata['gst'] = result
        
        if metadata.get('pan'):
            is_valid, result = validate_pan_number(metadata['pan'])
            if not is_valid:
                return jsonify({'error': result}), 400
            metadata['pan'] = result
        
        # Hash admin password
        hashed_password = hash_password(data['admin_password'])
        
        # Create tenant
        tenant = Tenant(
            name=data['name'],
            slug=slug,
            email=data['email'],
            phone=data.get('phone'),
            business_metadata=metadata,
            admin_name=data['admin_name'],
            admin_email=data['admin_email'],
            admin_password=hashed_password,
            subscription_status=data.get('subscription_status', 'trial')
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        return jsonify({
            'message': 'Tenant created successfully',
            'tenant': tenant.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/tenants/<int:tenant_id>', methods=['PUT'])
@token_required(user_types=['admin'])
def update_tenant(tenant_id):
    """Update tenant - Admin only"""
    try:
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        data = request.get_json()
        
        # Update basic fields
        if data.get('name'):
            tenant.name = data['name']
        
        if data.get('email'):
            is_valid, result = validate_email_format(data['email'])
            if not is_valid:
                return jsonify({'error': f'Invalid email: {result}'}), 400
            # Check if email already exists (excluding current tenant)
            existing = Tenant.query.filter_by(email=data['email']).first()
            if existing and existing.id != tenant_id:
                return jsonify({'error': 'Email already exists'}), 400
            tenant.email = result
        
        if data.get('phone'):
            is_valid, result = validate_phone_number(data['phone'])
            if not is_valid:
                return jsonify({'error': result}), 400
            tenant.phone = result
        
        if data.get('slug'):
            is_valid, message = validate_slug(data['slug'])
            if not is_valid:
                return jsonify({'error': message}), 400
            # Check if slug already exists (excluding current tenant)
            existing = Tenant.query.filter_by(slug=data['slug']).first()
            if existing and existing.id != tenant_id:
                return jsonify({'error': 'Slug already exists'}), 400
            tenant.slug = data['slug']
        
        if data.get('admin_name'):
            tenant.admin_name = data['admin_name']
        
        if data.get('admin_email'):
            is_valid, result = validate_email_format(data['admin_email'])
            if not is_valid:
                return jsonify({'error': f'Invalid admin email: {result}'}), 400
            existing = Tenant.query.filter_by(admin_email=data['admin_email']).first()
            if existing and existing.id != tenant_id:
                return jsonify({'error': 'Admin email already exists'}), 400
            tenant.admin_email = result
        
        if data.get('admin_password'):
            is_valid, message = validate_password_strength(data['admin_password'])
            if not is_valid:
                return jsonify({'error': message}), 400
            tenant.admin_password = hash_password(data['admin_password'])
        
        if 'is_active' in data:
            tenant.is_active = data['is_active']
        
        if data.get('subscription_status'):
            tenant.subscription_status = data['subscription_status']
        
        if data.get('metadata'):
            # Merge metadata
            current_metadata = tenant.business_metadata or {}
            current_metadata.update(data['metadata'])
            
            # Validate GST and PAN if provided
            if current_metadata.get('gst'):
                is_valid, result = validate_gst_number(current_metadata['gst'])
                if not is_valid:
                    return jsonify({'error': result}), 400
                current_metadata['gst'] = result
            
            if current_metadata.get('pan'):
                is_valid, result = validate_pan_number(current_metadata['pan'])
                if not is_valid:
                    return jsonify({'error': result}), 400
                current_metadata['pan'] = result
            
            tenant.business_metadata = current_metadata
        
        db.session.commit()
        
        return jsonify({
            'message': 'Tenant updated successfully',
            'tenant': tenant.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/tenants/<int:tenant_id>', methods=['DELETE'])
@token_required(user_types=['admin'])
def delete_tenant(tenant_id):
    """Delete tenant - Admin only"""
    try:
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        tenant_name = tenant.name
        
        # Delete tenant (users will be deleted due to cascade)
        db.session.delete(tenant)
        db.session.commit()
        
        return jsonify({
            'message': f'Tenant "{tenant_name}" deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/dashboard', methods=['GET'])
@token_required(user_types=['admin'])
def admin_dashboard():
    """Get admin dashboard stats"""
    try:
        total_tenants = Tenant.query.count()
        active_tenants = Tenant.query.filter_by(is_active=True).count()
        
        from app.models.user import User
        total_users = User.query.count()
        
        return jsonify({
            'stats': {
                'total_tenants': total_tenants,
                'active_tenants': active_tenants,
                'inactive_tenants': total_tenants - active_tenants,
                'total_users': total_users
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

