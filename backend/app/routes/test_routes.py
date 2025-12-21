from flask import Blueprint, request, jsonify, send_from_directory
from app.database import db
from app.models.test import Test, Question, TestResponse
from app.models.user import User
from app.utils.jwt_manager import token_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

# Create Blueprint
test_bp = Blueprint('test', __name__, url_prefix='/api/test')

def allowed_file(filename):
    """Check if file extension is allowed"""
    from app.config import Config
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# ==================== TENANT/ADMIN TEST MANAGEMENT ====================

@test_bp.route('/tests', methods=['GET'])
@token_required(user_types=['tenant', 'admin', 'user'])
def get_tests():
    """Get all tests for tenant/admin/user"""
    try:
        user_type = request.current_user.get('user_type')
        tenant_id = request.current_user.get('tenant_id')
        
        if user_type == 'admin':
            # Admin can see all tests
            tests = Test.query.filter_by(is_active=True).all()
        elif user_type == 'tenant' and tenant_id:
            # Tenant can see their tests
            tests = Test.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        elif user_type == 'user' and tenant_id:
            # User can see active tests from their tenant
            tests = Test.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        else:
            tests = []
        
        return jsonify({
            'tests': [test.to_dict() for test in tests]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@test_bp.route('/tests', methods=['POST'])
@token_required(user_types=['tenant', 'admin'])
def create_test():
    """Create a new test"""
    try:
        data = request.get_json()
        tenant_id = request.current_user.get('tenant_id') or data.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': 'tenant_id is required'}), 400
        
        if not data.get('title'):
            return jsonify({'error': 'title is required'}), 400
        
        test = Test(
            tenant_id=tenant_id,
            title=data['title'],
            description=data.get('description'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(test)
        db.session.commit()
        
        return jsonify({
            'message': 'Test created successfully',
            'test': test.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/tests/<int:test_id>', methods=['GET'])
@token_required(user_types=['tenant', 'admin', 'user'])
def get_test(test_id):
    """Get test with questions"""
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        test_dict = test.to_dict()
        test_dict['questions'] = [q.to_dict() for q in test.questions]
        
        return jsonify({'test': test_dict}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@test_bp.route('/tests/<int:test_id>', methods=['PUT'])
@token_required(user_types=['tenant', 'admin'])
def update_test(test_id):
    """Update test"""
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        data = request.get_json()
        if data.get('title'):
            test.title = data['title']
        if data.get('description') is not None:
            test.description = data['description']
        if 'is_active' in data:
            test.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Test updated successfully',
            'test': test.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/tests/<int:test_id>', methods=['DELETE'])
@token_required(user_types=['tenant', 'admin'])
def delete_test(test_id):
    """Delete test"""
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        db.session.delete(test)
        db.session.commit()
        
        return jsonify({'message': 'Test deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== QUESTION MANAGEMENT ====================

@test_bp.route('/tests/<int:test_id>/questions', methods=['GET'])
@token_required(user_types=['tenant', 'admin'])
def get_questions(test_id):
    """Get all questions for a test"""
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        questions = Question.query.filter_by(test_id=test_id).order_by(Question.priority_order).all()
        
        return jsonify({
            'questions': [q.to_dict() for q in questions]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@test_bp.route('/tests/<int:test_id>/questions', methods=['POST'])
@token_required(user_types=['tenant', 'admin'])
def create_question(test_id):
    """Create a new question"""
    try:
        test = Test.query.get(test_id)
        if not test:
            return jsonify({'error': 'Test not found'}), 404
        
        data = request.get_json()
        
        if not data.get('question_text'):
            return jsonify({'error': 'question_text is required'}), 400
        if not data.get('question_type'):
            return jsonify({'error': 'question_type is required'}), 400
        
        # Get next priority order
        max_priority = db.session.query(db.func.max(Question.priority_order)).filter_by(test_id=test_id).scalar() or 0
        
        question = Question(
            test_id=test_id,
            question_text=data['question_text'],
            question_type=data['question_type'],
            section=data.get('section'),
            options=data.get('options'),
            default_order=max_priority + 1,
            priority_order=data.get('priority_order', max_priority + 1),
            is_required=data.get('is_required', True),
            placeholder=data.get('placeholder')
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'message': 'Question created successfully',
            'question': question.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/questions/<int:question_id>', methods=['PUT'])
@token_required(user_types=['tenant', 'admin'])
def update_question(question_id):
    """Update question"""
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        data = request.get_json()
        if data.get('question_text'):
            question.question_text = data['question_text']
        if data.get('question_type'):
            question.question_type = data['question_type']
        if data.get('section') is not None:
            question.section = data['section']
        if data.get('options') is not None:
            question.options = data['options']
        if data.get('priority_order') is not None:
            question.priority_order = data['priority_order']
        if 'is_required' in data:
            question.is_required = data['is_required']
        if data.get('placeholder') is not None:
            question.placeholder = data['placeholder']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Question updated successfully',
            'question': question.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@token_required(user_types=['tenant', 'admin'])
def delete_question(question_id):
    """Delete question"""
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({'message': 'Question deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/tests/<int:test_id>/questions/reorder', methods=['POST'])
@token_required(user_types=['tenant', 'admin'])
def reorder_questions(test_id):
    """Update priority order of questions"""
    try:
        data = request.get_json()
        question_orders = data.get('question_orders', [])  # [{question_id: priority_order}, ...]
        
        for item in question_orders:
            question_id = item.get('question_id')
            priority_order = item.get('priority_order')
            if question_id and priority_order is not None:
                question = Question.query.get(question_id)
                if question and question.test_id == test_id:
                    question.priority_order = priority_order
        
        db.session.commit()
        
        return jsonify({'message': 'Questions reordered successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== USER TEST TAKING ====================

@test_bp.route('/tests/<int:test_id>/start', methods=['POST'])
@token_required(user_types=['user'])
def start_test(test_id):
    """Start a test - creates a new test response"""
    try:
        test = Test.query.get(test_id)
        if not test or not test.is_active:
            return jsonify({'error': 'Test not found or inactive'}), 404
        
        user_id = request.current_user['user_id']
        
        # Check if user already has an incomplete response
        existing_response = TestResponse.query.filter_by(
            test_id=test_id,
            user_id=user_id,
            is_completed=False
        ).first()
        
        if existing_response:
            return jsonify({
                'message': 'Test already started',
                'response': existing_response.to_dict()
            }), 200
        
        # Create new test response
        response = TestResponse(
            test_id=test_id,
            user_id=user_id,
            responses={},
            is_completed=False
        )
        
        db.session.add(response)
        db.session.commit()
        
        # Get test with questions ordered by priority
        test_dict = test.to_dict()
        test_dict['questions'] = [q.to_dict() for q in test.questions]
        
        return jsonify({
            'message': 'Test started',
            'response': response.to_dict(),
            'test': test_dict
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/responses/<int:response_id>/answers', methods=['POST'])
@token_required(user_types=['user'])
def submit_answer(response_id):
    """Submit answer to a question"""
    try:
        response = TestResponse.query.get(response_id)
        if not response:
            return jsonify({'error': 'Test response not found'}), 404
        
        if response.user_id != request.current_user['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if response.is_completed:
            return jsonify({'error': 'Test already completed'}), 400
        
        data = request.get_json()
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not question_id:
            return jsonify({'error': 'question_id is required'}), 400
        
        # Update responses dictionary
        responses = response.responses or {}
        responses[str(question_id)] = answer
        response.responses = responses
        
        db.session.commit()
        
        return jsonify({
            'message': 'Answer submitted successfully',
            'response': response.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/responses/<int:response_id>/upload-image', methods=['POST'])
@token_required(user_types=['user'])
def upload_image(response_id):
    """Upload image for test response"""
    try:
        from app.config import Config
        
        response = TestResponse.query.get(response_id)
        if not response:
            return jsonify({'error': 'Test response not found'}), 404
        
        if response.user_id != request.current_user['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to make filename unique
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{response_id}_{timestamp}_{filename}"
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(Config.UPLOAD_FOLDER, 'test_images')
            os.makedirs(upload_dir, exist_ok=True)
            
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # Update response
            response.image_path = filepath
            response.image_url = f"/api/test/uploads/{filename}"
            response.is_completed = True
            response.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'message': 'Image uploaded successfully',
                'response': response.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/responses/<int:response_id>/complete', methods=['POST'])
@token_required(user_types=['user'])
def complete_test(response_id):
    """Mark test as completed (without image upload)"""
    try:
        response = TestResponse.query.get(response_id)
        if not response:
            return jsonify({'error': 'Test response not found'}), 404
        
        if response.user_id != request.current_user['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        response.is_completed = True
        response.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Test completed successfully',
            'response': response.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@test_bp.route('/uploads/<filename>', methods=['GET'])
def get_uploaded_image(filename):
    """Serve uploaded images"""
    try:
        from app.config import Config
        
        # In Docker: working directory is /app
        # Uploads folder is at: /app/uploads/test_images
        app_root = os.getcwd()  # This will be /app in Docker
        upload_dir = os.path.join(app_root, Config.UPLOAD_FOLDER, 'test_images')
        
        # Ensure directory exists
        if not os.path.exists(upload_dir):
            return jsonify({'error': f'Upload directory not found: {upload_dir}'}), 404
        
        # Check if file exists
        file_path = os.path.join(upload_dir, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {filename}'}), 404
        
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@test_bp.route('/responses/<int:response_id>', methods=['GET'])
@token_required(user_types=['user'])
def get_test_response(response_id):
    """Get specific test response by ID"""
    try:
        user_id = request.current_user['user_id']
        response = TestResponse.query.get(response_id)
        
        if not response:
            return jsonify({'error': 'Test response not found'}), 404
        
        if response.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get test details with questions
        test = Test.query.get(response.test_id)
        response_dict = response.to_dict()
        if test:
            response_dict['test'] = test.to_dict()
            response_dict['test']['questions'] = [q.to_dict() for q in test.questions]
        
        return jsonify({
            'response': response_dict
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@test_bp.route('/responses', methods=['GET'])
@token_required(user_types=['user'])
def get_user_responses():
    """Get all test responses for current user"""
    try:
        user_id = request.current_user['user_id']
        responses = TestResponse.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'responses': [r.to_dict() for r in responses]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== INITIALIZE DEFAULT TEST ====================

@test_bp.route('/initialize-default-test', methods=['POST'])
@token_required(user_types=['tenant', 'admin'])
def initialize_default_test():
    """Initialize the Nutrition & Lifestyle Profile test with all questions"""
    try:
        from app.utils.create_default_test import create_default_test
        
        tenant_id = request.current_user.get('tenant_id') or request.get_json().get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': 'tenant_id is required'}), 400
        
        # Check if test already exists
        existing_test = Test.query.filter_by(
            tenant_id=tenant_id,
            title="Nutrition & Lifestyle Profile"
        ).first()
        
        if existing_test:
            return jsonify({
                'message': 'Default test already exists',
                'test': existing_test.to_dict()
            }), 200
        
        # Create default test
        test = create_default_test(tenant_id)
        
        return jsonify({
            'message': 'Default test created successfully',
            'test': test.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

