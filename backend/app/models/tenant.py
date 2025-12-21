from app.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Tenant(db.Model):
    """Tenant Model - Represents businesses/organizations using the platform"""
    
    __tablename__ = 'tenants'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)  # SEO-friendly URL
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Business Information stored as JSON metadata
    business_metadata = db.Column(JSON, nullable=True, default={})  # GST, PAN, Address, etc.
    
    # Tenant Admin Credentials
    admin_name = db.Column(db.String(255), nullable=False)
    admin_email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    admin_password = db.Column(db.String(255), nullable=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    subscription_status = db.Column(db.String(50), default='trial', nullable=False)  # trial, active, suspended, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = db.relationship('User', backref='tenant', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.name} - {self.slug}>'
    
    def to_dict(self, include_sensitive=False):
        """Convert tenant object to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'email': self.email,
            'phone': self.phone,
            'metadata': self.business_metadata,
            'admin_name': self.admin_name,
            'admin_email': self.admin_email,
            'is_active': self.is_active,
            'subscription_status': self.subscription_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include sensitive data only if explicitly requested
        if not include_sensitive:
            data.pop('admin_password', None)
        
        return data

