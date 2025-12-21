import jwt
from datetime import datetime, timedelta
from app.config import Config
from functools import wraps
from flask import request, jsonify

def create_access_token(user_id, user_type, email, tenant_id=None, role=None):
    """
    Create JWT access token
    
    Args:
        user_id: User's database ID
        user_type: Type of user ('admin', 'tenant', 'user')
        email: User's email
        tenant_id: Optional tenant ID (for users and tenants)
        role: Optional user role (for RBAC)
    
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user_id,
        'user_type': user_type,
        'email': email,
        'exp': datetime.utcnow() + timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': datetime.utcnow()
    }
    
    if tenant_id:
        payload['tenant_id'] = tenant_id
    
    if role:
        payload['role'] = role
    
    token = jwt.encode(
        payload,
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )
    
    return token

def decode_access_token(token):
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

def token_required(user_types=None):
    """
    Decorator to protect routes with JWT authentication
    
    Args:
        user_types: List of allowed user types ['admin', 'tenant', 'user']
                   If None, all authenticated users are allowed
    
    Usage:
        @token_required(user_types=['admin'])
        def admin_only_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Get token from Authorization header
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    # Expected format: "Bearer <token>"
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({'error': 'Invalid authorization header format'}), 401
            
            if not token:
                return jsonify({'error': 'Authorization token is missing'}), 401
            
            # Decode token
            payload = decode_access_token(token)
            
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Check user type if specified
            if user_types and payload.get('user_type') not in user_types:
                return jsonify({'error': 'Unauthorized access'}), 403
            
            # Add payload to request context for use in route
            request.current_user = payload
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

