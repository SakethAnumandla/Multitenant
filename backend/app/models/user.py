from app.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    """User Model - End users who interact with tenant services"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # User Information
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Profile Data
    profile_data = db.Column(JSON, nullable=True, default={})  # Age, gender, preferences, etc.
    
    # Role and Access
    role = db.Column(db.String(50), default='user', nullable=False)  # user, employee, manager, sales_rep, etc.
    access_level = db.Column(db.String(50), default='basic', nullable=False)  # basic, premium, admin
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Password Management
    temp_password = db.Column(db.String(255), nullable=True)  # For employee onboarding
    password_reset_required = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Unique constraint: email must be unique within a tenant
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'email', name='unique_tenant_user_email'),
    )
    
    def __repr__(self):
        return f'<User {self.email} - Tenant {self.tenant_id}>'
    
    def to_dict(self, include_sensitive=False):
        """Convert user object to dictionary"""
        data = {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'profile_data': self.profile_data,
            'role': self.role,
            'access_level': self.access_level,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'password_reset_required': self.password_reset_required,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include sensitive data only if explicitly requested
        if not include_sensitive:
            data.pop('password', None)
            data.pop('temp_password', None)
        
        return data

