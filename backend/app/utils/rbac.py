"""
Role-Based Access Control (RBAC) utilities
"""
from functools import wraps
from flask import request, jsonify
from app.models.user import User
from app.models.access_matrix import AccessMatrix
from app.models.tenant import Tenant

def get_user_role_from_token():
    """Extract user role from JWT token or database"""
    if not hasattr(request, 'current_user'):
        return None
    
    user_id = request.current_user.get('user_id')
    user_type = request.current_user.get('user_type')
    tenant_id = request.current_user.get('tenant_id')
    
    if not user_id:
        return None
    
    # For admin, return admin role
    if user_type == 'admin':
        return 'super_admin'
    
    # For tenant, return tenant_admin
    if user_type == 'tenant':
        return 'tenant_admin'
    
    # For users, get role from database
    if user_type == 'user':
        user = User.query.get(user_id)
        if user:
            # Map user role to RBAC role
            role_mapping = {
                'user': 'user',
                'employee': 'employee',
                'manager': 'manager',
                'sales_rep': 'employee',
                'tenant': 'tenant_admin'
            }
            return role_mapping.get(user.role, 'user')
    
    return None

def get_user_tenant_id():
    """Get tenant_id from token or user record"""
    if not hasattr(request, 'current_user'):
        return None
    
    tenant_id = request.current_user.get('tenant_id')
    if tenant_id:
        return tenant_id
    
    user_id = request.current_user.get('user_id')
    user_type = request.current_user.get('user_type')
    
    if user_type == 'user' and user_id:
        user = User.query.get(user_id)
        if user:
            return user.tenant_id
    
    return None

def has_permission(role, tenant_id, resource, action):
    """
    Check if a role has permission for a resource and action
    
    Args:
        role: User role (super_admin, tenant_admin, manager, employee, user)
        tenant_id: Tenant ID (for tenant-specific permissions)
        resource: Resource name (employees, users, tests, reports, etc.)
        action: Action (create, read, update, delete)
    
    Returns:
        True if permission exists, False otherwise
    """
    # Super admin has all permissions
    if role == 'super_admin':
        return True
    
    # Tenant admin has all permissions for their tenant
    if role == 'tenant_admin':
        return True
    
    # Get access matrix for this role and tenant
    # First try tenant-specific, then global
    matrix = None
    if tenant_id:
        matrix = AccessMatrix.query.filter_by(
            tenant_id=tenant_id,
            role=role,
            is_active=True
        ).first()
    
    if not matrix:
        # Try global/default permissions
        matrix = AccessMatrix.query.filter_by(
            tenant_id=None,
            role=role,
            is_active=True
        ).first()
    
    if not matrix:
        return False
    
    return matrix.has_permission(resource, action)

def permission_required(resource, action):
    """
    Decorator to check if user has permission for a resource and action
    
    Usage:
        @permission_required('employees', 'create')
        def create_employee():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user role and tenant
            role = get_user_role_from_token()
            tenant_id = get_user_tenant_id()
            
            if not role:
                return jsonify({'error': 'Unable to determine user role'}), 403
            
            # Check permission
            if not has_permission(role, tenant_id, resource, action):
                return jsonify({
                    'error': f'Access denied. {role} does not have {action} permission for {resource}'
                }), 403
            
            # Add role to request context for use in route
            request.current_user_role = role
            request.current_user_tenant_id = tenant_id
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def role_required(*allowed_roles):
    """
    Decorator to check if user has one of the required roles
    
    Usage:
        @role_required('super_admin', 'manager')
        def admin_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            role = get_user_role_from_token()
            
            if not role:
                return jsonify({'error': 'Unable to determine user role'}), 403
            
            if role not in allowed_roles:
                return jsonify({
                    'error': f'Access denied. Required roles: {", ".join(allowed_roles)}, got: {role}'
                }), 403
            
            request.current_user_role = role
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def get_default_permissions():
    """Get default access matrix permissions"""
    return {
        'super_admin': {
            'employees': ['create', 'read', 'update', 'delete'],
            'users': ['create', 'read', 'update', 'delete'],
            'tests': ['create', 'read', 'update', 'delete'],
            'reports': ['create', 'read', 'update', 'delete'],
            'tenants': ['create', 'read', 'update', 'delete']
        },
        'tenant_admin': {
            'employees': ['create', 'read', 'update', 'delete'],
            'users': ['create', 'read', 'update', 'delete'],
            'tests': ['create', 'read', 'update', 'delete'],
            'reports': ['read'],
            'tenants': ['read', 'update']  # Can only update own tenant
        },
        'manager': {
            'employees': ['read', 'update'],
            'users': ['create', 'read', 'update'],
            'tests': ['read'],
            'reports': ['read']
        },
        'employee': {
            'employees': ['read'],
            'users': ['read', 'update'],
            'tests': ['create', 'read', 'update'],
            'reports': []
        },
        'user': {
            'employees': [],
            'users': ['read', 'update'],  # Can only update own profile
            'tests': ['read'],
            'reports': []
        }
    }

