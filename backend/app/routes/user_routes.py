from flask import Blueprint, request, jsonify
from app.database import db
from app.models.user import User
from app.models.tenant import Tenant
from app.utils.auth import authenticate_user, hash_password, verify_password
from app.utils.jwt_manager import create_access_token, token_required
from app.utils.validators import validate_email_format, validate_password_strength, validate_phone_number

# Create Blueprint
user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/login', methods=['POST'])
def user_login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        tenant_id = data.get('tenant_id')  # Optional: can login via tenant slug or ID
        
        # Authenticate user
        user = authenticate_user(email, password, tenant_id)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if password reset is required
        if user.password_reset_required:
            return jsonify({
                'message': 'Password reset required',
                'password_reset_required': True,
                'user_id': user.id,
                'temp_login': True
            }), 200
        
        # Map user role to RBAC role
        role_mapping = {
            'user': 'user',
            'employee': 'employee',
            'manager': 'manager',
            'sales_rep': 'employee',
            'tenant': 'tenant_admin'
        }
        rbac_role = role_mapping.get(user.role, 'user')
        
        # Create JWT token
        token = create_access_token(
            user_id=user.id,
            user_type='user',
            email=user.email,
            tenant_id=user.tenant_id,
            role=rbac_role
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/login/<slug>', methods=['POST'])
def user_login_by_slug(slug):
    """User login via tenant slug (SEO-friendly)"""
    try:
        # Find tenant by slug
        tenant = Tenant.query.filter_by(slug=slug, is_active=True).first()
        
        if not tenant:
            return jsonify({'error': 'Tenant not found or inactive'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email']
        password = data['password']
        
        # Authenticate user for this specific tenant
        user = authenticate_user(email, password, tenant.id)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if password reset is required
        if user.password_reset_required:
            return jsonify({
                'message': 'Password reset required',
                'password_reset_required': True,
                'user_id': user.id,
                'temp_login': True
            }), 200
        
        # Map user role to RBAC role
        role_mapping = {
            'user': 'user',
            'employee': 'employee',
            'manager': 'manager',
            'sales_rep': 'employee',
            'tenant': 'tenant_admin'
        }
        rbac_role = role_mapping.get(user.role, 'user')
        
        # Create JWT token
        token = create_access_token(
            user_id=user.id,
            user_type='user',
            email=user.email,
            tenant_id=user.tenant_id,
            role=rbac_role
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict(),
            'tenant': tenant.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password for first-time employee login"""
    try:
        data = request.get_json()
        
        if not data.get('user_id') or not data.get('temp_password') or not data.get('new_password'):
            return jsonify({'error': 'user_id, temp_password, and new_password are required'}), 400
        
        user = User.query.get(data['user_id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify temp password
        if not user.temp_password or not verify_password(data['temp_password'], user.password):
            return jsonify({'error': 'Invalid temporary password'}), 401
        
        # Validate new password
        is_valid, message = validate_password_strength(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Update password
        user.password = hash_password(data['new_password'])
        user.temp_password = None
        user.password_reset_required = False
        
        db.session.commit()
        
        # Map user role to RBAC role
        role_mapping = {
            'user': 'user',
            'employee': 'employee',
            'manager': 'manager',
            'sales_rep': 'employee',
            'tenant': 'tenant_admin'
        }
        rbac_role = role_mapping.get(user.role, 'user')
        
        # Create JWT token for automatic login
        token = create_access_token(
            user_id=user.id,
            user_type='user',
            email=user.email,
            tenant_id=user.tenant_id,
            role=rbac_role
        )
        
        return jsonify({
            'message': 'Password reset successful',
            'token': token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/register', methods=['POST'])
def user_register():
    """User self-registration (for public signup)"""
    try:
        data = request.get_json()
        
        # Required: tenant_id or slug
        tenant = None
        if data.get('tenant_id'):
            tenant = Tenant.query.get(data['tenant_id'])
        elif data.get('tenant_slug'):
            tenant = Tenant.query.filter_by(slug=data['tenant_slug']).first()
        
        if not tenant:
            return jsonify({'error': 'Valid tenant_id or tenant_slug is required'}), 400
        
        if not tenant.is_active:
            return jsonify({'error': 'Tenant is not active'}), 400
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email
        is_valid, result = validate_email_format(data['email'])
        if not is_valid:
            return jsonify({'error': f'Invalid email: {result}'}), 400
        
        # Check if user already exists
        existing = User.query.filter_by(
            tenant_id=tenant.id,
            email=data['email']
        ).first()
        
        if existing:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Validate password
        is_valid, message = validate_password_strength(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Validate phone if provided
        if data.get('phone'):
            is_valid, result = validate_phone_number(data['phone'])
            if not is_valid:
                return jsonify({'error': result}), 400
            data['phone'] = result
        
        # Create user
        user = User(
            tenant_id=tenant.id,
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            password=hash_password(data['password']),
            role='user',
            access_level='basic',
            profile_data=data.get('profile_data', {})
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Map user role to RBAC role
        role_mapping = {
            'user': 'user',
            'employee': 'employee',
            'manager': 'manager',
            'sales_rep': 'employee',
            'tenant': 'tenant_admin'
        }
        rbac_role = role_mapping.get(user.role, 'user')
        
        # Create JWT token for automatic login
        token = create_access_token(
            user_id=user.id,
            user_type='user',
            email=user.email,
            tenant_id=user.tenant_id,
            role=rbac_role
        )
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@token_required(user_types=['user'])
def get_user_profile():
    """Get user profile"""
    try:
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@token_required(user_types=['user'])
def update_user_profile():
    """Update user profile"""
    try:
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if data.get('name'):
            user.name = data['name']
        
        if data.get('phone'):
            is_valid, result = validate_phone_number(data['phone'])
            if not is_valid:
                return jsonify({'error': result}), 400
            user.phone = result
        
        if data.get('profile_data'):
            current_profile = user.profile_data or {}
            current_profile.update(data['profile_data'])
            user.profile_data = current_profile
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/change-password', methods=['POST'])
@token_required(user_types=['user'])
def change_password():
    """Change user password"""
    try:
        user_id = request.current_user['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'old_password and new_password are required'}), 400
        
        # Verify old password
        if not verify_password(data['old_password'], user.password):
            return jsonify({'error': 'Invalid old password'}), 401
        
        # Validate new password
        is_valid, message = validate_password_strength(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Update password
        user.password = hash_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

