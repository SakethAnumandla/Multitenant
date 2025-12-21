"""
Utility to initialize default RBAC access matrix
Run this on app startup or via API endpoint
"""
from app.database import db
from app.models.access_matrix import AccessMatrix
from app.utils.rbac import get_default_permissions

def initialize_default_access_matrix(tenant_id=None):
    """
    Initialize default access matrix for all roles
    
    Args:
        tenant_id: Optional tenant ID. If None, creates global permissions.
    
    Returns:
        dict with created and updated role counts
    """
    default_perms = get_default_permissions()
    
    created = []
    updated = []
    
    for role, permissions in default_perms.items():
        # Skip super_admin if tenant_id is provided (super_admin is global only)
        if role == 'super_admin' and tenant_id is not None:
            continue
        
        # Check if matrix already exists
        existing = None
        if tenant_id:
            existing = AccessMatrix.query.filter_by(
                tenant_id=tenant_id,
                role=role
            ).first()
        else:
            existing = AccessMatrix.query.filter_by(
                tenant_id=None,
                role=role
            ).first()
        
        if existing:
            # Update existing
            existing.permissions = permissions
            existing.is_active = True
            updated.append(role)
        else:
            # Create new
            matrix = AccessMatrix(
                tenant_id=tenant_id if tenant_id else None,
                role=role,
                permissions=permissions,
                description=f'Default permissions for {role}',
                is_active=True
            )
            db.session.add(matrix)
            created.append(role)
    
    db.session.commit()
    
    return {
        'created': created,
        'updated': updated,
        'total': len(created) + len(updated)
    }

