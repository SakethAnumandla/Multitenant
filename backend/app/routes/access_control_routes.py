from flask import Blueprint, request, jsonify
from app.database import db
from app.models.access_matrix import AccessMatrix
from app.utils.jwt_manager import token_required
from app.utils.rbac import role_required, get_user_tenant_id, get_default_permissions

# Create Blueprint
access_control_bp = Blueprint('access_control', __name__, url_prefix='/api/access-control')

@access_control_bp.route('/matrix', methods=['GET'])
@token_required(user_types=['tenant', 'admin', 'user'])
def get_access_matrix():
    """Get access matrix for a role or all roles"""
    try:
        tenant_id = get_user_tenant_id()
        role_filter = request.args.get('role')
        
        if role_filter:
            # Get specific role permissions
            if tenant_id:
                matrix = AccessMatrix.query.filter_by(
                    tenant_id=tenant_id,
                    role=role_filter,
                    is_active=True
                ).first()
            else:
                matrix = AccessMatrix.query.filter_by(
                    tenant_id=None,
                    role=role_filter,
                    is_active=True
                ).first()
            
            if not matrix:
                return jsonify({'error': f'Access matrix not found for role: {role_filter}'}), 404
            
            return jsonify({'access_matrix': matrix.to_dict()}), 200
        else:
            # Get all access matrices
            query = AccessMatrix.query.filter_by(is_active=True)
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            
            matrices = query.all()
            
            return jsonify({
                'access_matrices': [m.to_dict() for m in matrices]
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@access_control_bp.route('/matrix', methods=['POST'])
@token_required(user_types=['tenant', 'admin'])
@role_required('tenant_admin', 'super_admin')
def create_access_matrix():
    """Create or update access matrix for a role"""
    try:
        tenant_id = get_user_tenant_id()
        data = request.get_json()
        
        if not data.get('role'):
            return jsonify({'error': 'role is required'}), 400
        
        if not data.get('permissions'):
            return jsonify({'error': 'permissions is required'}), 400
        
        role = data['role']
        
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
            existing.permissions = data['permissions']
            existing.description = data.get('description')
            existing.is_active = data.get('is_active', True)
            db.session.commit()
            
            return jsonify({
                'message': 'Access matrix updated successfully',
                'access_matrix': existing.to_dict()
            }), 200
        else:
            # Create new
            matrix = AccessMatrix(
                tenant_id=tenant_id if tenant_id else None,
                role=role,
                permissions=data['permissions'],
                description=data.get('description'),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(matrix)
            db.session.commit()
            
            return jsonify({
                'message': 'Access matrix created successfully',
                'access_matrix': matrix.to_dict()
            }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@access_control_bp.route('/matrix/<int:matrix_id>', methods=['PUT'])
@token_required(user_types=['tenant', 'admin'])
@role_required('tenant_admin', 'super_admin')
def update_access_matrix(matrix_id):
    """Update access matrix"""
    try:
        matrix = AccessMatrix.query.get(matrix_id)
        if not matrix:
            return jsonify({'error': 'Access matrix not found'}), 404
        
        tenant_id = get_user_tenant_id()
        # Check if user can modify this matrix
        if matrix.tenant_id and matrix.tenant_id != tenant_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if data.get('permissions'):
            matrix.permissions = data['permissions']
        
        if data.get('description') is not None:
            matrix.description = data['description']
        
        if 'is_active' in data:
            matrix.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Access matrix updated successfully',
            'access_matrix': matrix.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@access_control_bp.route('/initialize-default-matrix', methods=['POST'])
@token_required(user_types=['tenant', 'admin'])
@role_required('tenant_admin', 'super_admin')
def initialize_default_matrix():
    """Initialize default access matrix for all roles"""
    try:
        tenant_id = get_user_tenant_id()
        default_perms = get_default_permissions()
        
        created = []
        updated = []
        
        for role, permissions in default_perms.items():
            # Skip super_admin if not admin
            if role == 'super_admin' and not tenant_id is None:
                continue
            
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
                existing.permissions = permissions
                existing.is_active = True
                updated.append(role)
            else:
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
        
        return jsonify({
            'message': 'Default access matrix initialized',
            'created': created,
            'updated': updated
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@access_control_bp.route('/check-permission', methods=['POST'])
@token_required(user_types=['tenant', 'admin', 'user'])
def check_permission():
    """Check if current user has permission for a resource and action"""
    try:
        from app.utils.rbac import get_user_role_from_token, has_permission, get_user_tenant_id
        
        data = request.get_json()
        resource = data.get('resource')
        action = data.get('action')
        
        if not resource or not action:
            return jsonify({'error': 'resource and action are required'}), 400
        
        role = get_user_role_from_token()
        tenant_id = get_user_tenant_id()
        
        if not role:
            return jsonify({'error': 'Unable to determine user role'}), 403
        
        has_access = has_permission(role, tenant_id, resource, action)
        
        return jsonify({
            'has_permission': has_access,
            'role': role,
            'resource': resource,
            'action': action
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

