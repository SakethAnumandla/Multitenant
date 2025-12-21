from app.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class AccessMatrix(db.Model):
    """Access Control Matrix - Defines permissions for each role"""
    
    __tablename__ = 'access_matrix'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=True, index=True)
    # If tenant_id is null, it's a global/default permission
    
    # Role Information
    role = db.Column(db.String(50), nullable=False, index=True)  # super_admin, manager, employee, user
    
    # Permissions stored as JSON
    # Format: {"resource": ["create", "read", "update", "delete"], ...}
    permissions = db.Column(JSON, nullable=False, default={})
    
    # Metadata
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Unique constraint: role must be unique per tenant (or global if tenant_id is null)
    __table_args__ = (
        db.UniqueConstraint('tenant_id', 'role', name='unique_tenant_role'),
    )
    
    def __repr__(self):
        tenant_info = f"Tenant {self.tenant_id}" if self.tenant_id else "Global"
        return f'<AccessMatrix {self.role} - {tenant_info}>'
    
    def to_dict(self):
        """Convert access matrix to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'role': self.role,
            'permissions': self.permissions,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def has_permission(self, resource, action):
        """Check if this role has permission for a resource and action"""
        if not self.is_active:
            return False
        
        resource_perms = self.permissions.get(resource, [])
        return action in resource_perms or 'all' in resource_perms

