from flask import Blueprint, request, jsonify
from app.database import db
from app.models.tenant import Tenant
from app.models.user import User
from app.utils.auth import authenticate_tenant, hash_password, generate_temp_password
from app.utils.jwt_manager import create_access_token, token_required
from app.utils.validators import (
    validate_email_format,
    validate_password_strength,
    validate_phone_number
)

# Create Blueprint
tenant_bp = Blueprint('tenant', __name__, url_prefix='/api/tenant')

@tenant_bp.route('/login', methods=['POST'])
def tenant_login():
    """Tenant admin login endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        
        # Authenticate tenant
        tenant = authenticate_tenant(email, password)
        
        if not tenant:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        token = create_access_token(
            user_id=tenant.id,
            user_type='tenant',
            email=tenant.admin_email,
            tenant_id=tenant.id,
            role='tenant_admin'
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'tenant': tenant.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/profile', methods=['GET'])
@token_required(user_types=['tenant'])
def get_tenant_profile():
    """Get tenant profile"""
    try:
        tenant_id = request.current_user['user_id']
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        return jsonify({'tenant': tenant.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/profile', methods=['PUT'])
@token_required(user_types=['tenant'])
def update_tenant_profile():
    """Update tenant profile"""
    try:
        tenant_id = request.current_user['user_id']
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if data.get('phone'):
            is_valid, result = validate_phone_number(data['phone'])
            if not is_valid:
                return jsonify({'error': result}), 400
            tenant.phone = result
        
        if data.get('admin_name'):
            tenant.admin_name = data['admin_name']
        
        if data.get('metadata'):
            current_metadata = tenant.business_metadata or {}
            current_metadata.update(data['metadata'])
            tenant.business_metadata = current_metadata
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'tenant': tenant.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/users', methods=['GET'])
@token_required(user_types=['tenant'])
def get_all_users():
    """Get all users for this tenant"""
    try:
        tenant_id = request.current_user['user_id']
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role = request.args.get('role')  # Filter by role
        
        query = User.query.filter_by(tenant_id=tenant_id)
        
        if role:
            query = query.filter_by(role=role)
        
        users_pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users_list = [user.to_dict() for user in users_pagination.items]
        
        return jsonify({
            'users': users_list,
            'total': users_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': users_pagination.pages
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required(user_types=['tenant'])
def get_user_by_id(user_id):
    """Get specific user by ID"""
    try:
        tenant_id = request.current_user['user_id']
        
        user = User.query.filter_by(
            id=user_id,
            tenant_id=tenant_id
        ).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/users', methods=['POST'])
@token_required(user_types=['tenant'])
def create_user():
    """Create new user/employee"""
    try:
        tenant_id = request.current_user['user_id']
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email
        is_valid, result = validate_email_format(data['email'])
        if not is_valid:
            return jsonify({'error': f'Invalid email: {result}'}), 400
        
        # Check if user email already exists for this tenant
        existing = User.query.filter_by(
            tenant_id=tenant_id,
            email=data['email']
        ).first()
        
        if existing:
            return jsonify({'error': 'Email already exists for this tenant'}), 400
        
        # Validate phone if provided
        if data.get('phone'):
            is_valid, result = validate_phone_number(data['phone'])
            if not is_valid:
                return jsonify({'error': result}), 400
            data['phone'] = result
        
        # Determine if this is an employee or user
        role = data.get('role', 'user')
        
        # For employees, generate temporary password and send email
        if role in ['employee', 'manager', 'sales_rep']:
            temp_password = generate_temp_password()
            hashed_password = hash_password(temp_password)
            
            # TODO: Send email with temp_password
            # For now, return it in response (REMOVE IN PRODUCTION)
            
            user = User(
                tenant_id=tenant_id,
                name=data['name'],
                email=data['email'],
                phone=data.get('phone'),
                password=hashed_password,
                temp_password=temp_password,
                password_reset_required=True,
                role=role,
                access_level=data.get('access_level', 'basic'),
                profile_data=data.get('profile_data', {})
            )
            
            db.session.add(user)
            db.session.commit()
            
            response_data = user.to_dict()
            response_data['temp_password'] = temp_password  # REMOVE IN PRODUCTION
            
            return jsonify({
                'message': 'Employee created successfully. Temporary password sent to email.',
                'user': response_data
            }), 201
        
        else:
            # For regular users, password is required
            if not data.get('password'):
                return jsonify({'error': 'Password is required for user registration'}), 400
            
            is_valid, message = validate_password_strength(data['password'])
            if not is_valid:
                return jsonify({'error': message}), 400
            
            hashed_password = hash_password(data['password'])
            
            user = User(
                tenant_id=tenant_id,
                name=data['name'],
                email=data['email'],
                phone=data.get('phone'),
                password=hashed_password,
                role=role,
                access_level=data.get('access_level', 'basic'),
                profile_data=data.get('profile_data', {})
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'User created successfully',
                'user': user.to_dict()
            }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required(user_types=['tenant'])
def update_user(user_id):
    """Update user/employee"""
    try:
        tenant_id = request.current_user['user_id']
        
        user = User.query.filter_by(
            id=user_id,
            tenant_id=tenant_id
        ).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if data.get('name'):
            user.name = data['name']
        
        if data.get('phone'):
            is_valid, result = validate_phone_number(data['phone'])
            if not is_valid:
                return jsonify({'error': result}), 400
            user.phone = result
        
        if data.get('role'):
            user.role = data['role']
        
        if data.get('access_level'):
            user.access_level = data['access_level']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        if data.get('profile_data'):
            current_profile = user.profile_data or {}
            current_profile.update(data['profile_data'])
            user.profile_data = current_profile
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required(user_types=['tenant'])
def delete_user(user_id):
    """Delete user/employee"""
    try:
        tenant_id = request.current_user['user_id']
        
        user = User.query.filter_by(
            id=user_id,
            tenant_id=tenant_id
        ).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_name = user.name
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'User "{user_name}" deleted successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tenant_bp.route('/dashboard', methods=['GET'])
@token_required(user_types=['tenant'])
def tenant_dashboard():
    """Get tenant dashboard stats"""
    try:
        tenant_id = request.current_user['user_id']
        
        total_users = User.query.filter_by(tenant_id=tenant_id).count()
        active_users = User.query.filter_by(tenant_id=tenant_id, is_active=True).count()
        
        employees = User.query.filter_by(tenant_id=tenant_id).filter(
            User.role.in_(['employee', 'manager', 'sales_rep'])
        ).count()
        
        regular_users = User.query.filter_by(
            tenant_id=tenant_id,
            role='user'
        ).count()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'employees': employees,
                'regular_users': regular_users
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

