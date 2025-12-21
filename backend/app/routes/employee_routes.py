from flask import Blueprint, request, jsonify
from app.database import db
from app.models.user import User
from app.utils.jwt_manager import token_required
from app.utils.rbac import permission_required, role_required, get_user_role_from_token, get_user_tenant_id
from app.utils.auth import hash_password, generate_temp_password
from app.utils.validators import validate_email_format, validate_password_strength, validate_phone_number

# Create Blueprint
employee_bp = Blueprint('employee', __name__, url_prefix='/api/tenant/employees')

@employee_bp.route('', methods=['GET'])
@token_required(user_types=['tenant', 'user'])
@permission_required('employees', 'read')
def get_all_employees():
    """Get all employees for this tenant"""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant ID not found'}), 400
        
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role_filter = request.args.get('role')  # Filter by role
        
        # Query employees (exclude regular users)
        query = User.query.filter_by(tenant_id=tenant_id).filter(
            User.role.in_(['employee', 'manager', 'sales_rep'])
        )
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        employees_pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        employees_list = [emp.to_dict() for emp in employees_pagination.items]
        
        return jsonify({
            'employees': employees_list,
            'total': employees_pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': employees_pagination.pages
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employee_bp.route('/<int:employee_id>', methods=['GET'])
@token_required(user_types=['tenant', 'user'])
@permission_required('employees', 'read')
def get_employee_by_id(employee_id):
    """Get specific employee by ID"""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant ID not found'}), 400
        
        employee = User.query.filter_by(
            id=employee_id,
            tenant_id=tenant_id
        ).filter(User.role.in_(['employee', 'manager', 'sales_rep'])).first()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        return jsonify({'employee': employee.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@employee_bp.route('', methods=['POST'])
@token_required(user_types=['tenant', 'user'])
@permission_required('employees', 'create')
def create_employee():
    """Create new employee - Requires 'create' permission on 'employees'"""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant ID not found'}), 400
        
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
        
        # Check if employee email already exists for this tenant
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
        
        # Employee role validation
        role = data.get('role', 'employee')
        if role not in ['employee', 'manager', 'sales_rep']:
            return jsonify({'error': 'Invalid role. Must be: employee, manager, or sales_rep'}), 400
        
        # Generate temporary password for employee onboarding
        temp_password = generate_temp_password()
        hashed_password = hash_password(temp_password)
        
        # TODO: Send email with temp_password
        # For now, return it in response (REMOVE IN PRODUCTION)
        
        employee = User(
            tenant_id=tenant_id,
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            password=hashed_password,
            temp_password=temp_password,
            password_reset_required=True,
            role=role,
            access_level=data.get('access_level', 'basic'),
            profile_data=data.get('profile_data', {}),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(employee)
        db.session.commit()
        
        response_data = employee.to_dict()
        response_data['temp_password'] = temp_password  # REMOVE IN PRODUCTION
        
        return jsonify({
            'message': 'Employee created successfully. Temporary password sent to email.',
            'employee': response_data
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employee_bp.route('/<int:employee_id>', methods=['PUT'])
@token_required(user_types=['tenant', 'user'])
@permission_required('employees', 'update')
def update_employee(employee_id):
    """Update employee - Requires 'update' permission on 'employees'"""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant ID not found'}), 400
        
        employee = User.query.filter_by(
            id=employee_id,
            tenant_id=tenant_id
        ).filter(User.role.in_(['employee', 'manager', 'sales_rep'])).first()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Check if manager trying to update - they can't change role or delete
        current_role = get_user_role_from_token()
        data = request.get_json()
        
        # Managers cannot change employee roles
        if current_role == 'manager' and data.get('role'):
            if data['role'] != employee.role:
                return jsonify({
                    'error': 'Managers cannot change employee roles'
                }), 403
        
        # Update fields
        if data.get('name'):
            employee.name = data['name']
        
        if data.get('phone'):
            is_valid, result = validate_phone_number(data['phone'])
            if not is_valid:
                return jsonify({'error': result}), 400
            employee.phone = result
        
        # Role update (only allowed for tenant_admin/super_admin)
        if data.get('role') and current_role in ['tenant_admin', 'super_admin']:
            if data['role'] not in ['employee', 'manager', 'sales_rep']:
                return jsonify({'error': 'Invalid role'}), 400
            employee.role = data['role']
        
        if data.get('access_level'):
            employee.access_level = data['access_level']
        
        if 'is_active' in data:
            # Managers cannot deactivate employees
            if current_role == 'manager':
                return jsonify({
                    'error': 'Managers cannot deactivate employees'
                }), 403
            employee.is_active = data['is_active']
        
        if data.get('profile_data'):
            current_profile = employee.profile_data or {}
            current_profile.update(data['profile_data'])
            employee.profile_data = current_profile
        
        db.session.commit()
        
        return jsonify({
            'message': 'Employee updated successfully',
            'employee': employee.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employee_bp.route('/<int:employee_id>', methods=['DELETE'])
@token_required(user_types=['tenant', 'user'])
@permission_required('employees', 'delete')
def delete_employee(employee_id):
    """Delete (deactivate) employee - Requires 'delete' permission on 'employees'"""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant ID not found'}), 400
        
        employee = User.query.filter_by(
            id=employee_id,
            tenant_id=tenant_id
        ).filter(User.role.in_(['employee', 'manager', 'sales_rep'])).first()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        current_role = get_user_role_from_token()
        
        # Managers cannot delete employees
        if current_role == 'manager':
            return jsonify({
                'error': 'Managers cannot delete employees. Only tenant admins can delete.'
            }), 403
        
        # Soft delete - set is_active to False
        employee_name = employee.name
        employee.is_active = False
        
        db.session.commit()
        
        return jsonify({
            'message': f'Employee "{employee_name}" deactivated successfully'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@employee_bp.route('/<int:employee_id>/assign-role', methods=['POST'])
@token_required(user_types=['tenant', 'user'])
@role_required('tenant_admin', 'super_admin')
def assign_role(employee_id):
    """Assign role to employee - Only tenant_admin/super_admin"""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'error': 'Tenant ID not found'}), 400
        
        employee = User.query.filter_by(
            id=employee_id,
            tenant_id=tenant_id
        ).first()
        
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'role is required'}), 400
        
        if new_role not in ['employee', 'manager', 'sales_rep']:
            return jsonify({'error': 'Invalid role. Must be: employee, manager, or sales_rep'}), 400
        
        employee.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': f'Role assigned successfully. Employee is now {new_role}',
            'employee': employee.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

