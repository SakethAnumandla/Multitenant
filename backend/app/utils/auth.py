import bcrypt
from app.models.admin import Admin
from app.models.tenant import Tenant
from app.models.user import User

def hash_password(password):
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password, hashed_password):
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def authenticate_admin(email, password):
    """
    Authenticate admin user
    
    Args:
        email: Admin email
        password: Admin password
    
    Returns:
        Admin object if authentication successful, None otherwise
    """
    admin = Admin.query.filter_by(email=email, is_active=True).first()
    
    if admin and verify_password(password, admin.password):
        return admin
    
    return None

def authenticate_tenant(email, password):
    """
    Authenticate tenant admin user
    
    Args:
        email: Tenant admin email
        password: Tenant admin password
    
    Returns:
        Tenant object if authentication successful, None otherwise
    """
    tenant = Tenant.query.filter_by(admin_email=email, is_active=True).first()
    
    if tenant and verify_password(password, tenant.admin_password):
        return tenant
    
    return None

def authenticate_user(email, password, tenant_id=None):
    """
    Authenticate user
    
    Args:
        email: User email
        password: User password
        tenant_id: Optional tenant ID to scope the search
    
    Returns:
        User object if authentication successful, None otherwise
    """
    query = User.query.filter_by(email=email, is_active=True)
    
    if tenant_id:
        query = query.filter_by(tenant_id=tenant_id)
    
    user = query.first()
    
    if user and verify_password(password, user.password):
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        from app.database import db
        db.session.commit()
        return user
    
    return None

def generate_temp_password():
    """
    Generate a temporary password for new employees
    
    Returns:
        Temporary password string
    """
    import secrets
    import string
    
    # Generate 12 character password with letters, digits, and special characters
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(alphabet) for i in range(12))
    
    return password

