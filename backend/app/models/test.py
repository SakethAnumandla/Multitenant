from app.database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Test(db.Model):
    """Test/Questionnaire Model"""
    
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Test Information
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    questions = db.relationship('Question', backref='test', lazy=True, cascade='all, delete-orphan', order_by='Question.priority_order')
    responses = db.relationship('TestResponse', backref='test', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Test {self.title} - Tenant {self.tenant_id}>'
    
    def to_dict(self):
        """Convert test object to dictionary"""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'title': self.title,
            'description': self.description,
            'is_active': self.is_active,
            'questions_count': len(self.questions),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Question(db.Model):
    """Question Model"""
    
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Question Information
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # text, radio, checkbox, range, textarea
    section = db.Column(db.String(100), nullable=True)  # Section A, B, C, etc.
    
    # Options for radio/checkbox
    options = db.Column(JSON, nullable=True)  # List of options for radio/checkbox
    
    # Ordering
    default_order = db.Column(db.Integer, nullable=False)  # Original order
    priority_order = db.Column(db.Integer, nullable=False)  # User-defined priority order
    
    # Settings
    is_required = db.Column(db.Boolean, default=True, nullable=False)
    placeholder = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Question {self.id} - {self.question_text[:50]}>'
    
    def to_dict(self):
        """Convert question object to dictionary"""
        return {
            'id': self.id,
            'test_id': self.test_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'section': self.section,
            'options': self.options,
            'default_order': self.default_order,
            'priority_order': self.priority_order,
            'is_required': self.is_required,
            'placeholder': self.placeholder,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TestResponse(db.Model):
    """Test Response Model - Stores user responses to tests"""
    
    __tablename__ = 'test_responses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Responses
    responses = db.Column(JSON, nullable=False, default={})  # {question_id: answer}
    
    # Image Upload
    image_path = db.Column(db.String(500), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    
    # Status
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='test_responses')
    
    def __repr__(self):
        return f'<TestResponse {self.id} - User {self.user_id} - Test {self.test_id}>'
    
    def to_dict(self):
        """Convert test response object to dictionary"""
        return {
            'id': self.id,
            'test_id': self.test_id,
            'user_id': self.user_id,
            'responses': self.responses,
            'image_path': self.image_path,
            'image_url': self.image_url,
            'is_completed': self.is_completed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

