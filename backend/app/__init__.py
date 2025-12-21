from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import db, init_db

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize database
    init_db(app)
    
    # Configure file upload
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Register blueprints
    from app.routes.admin_routes import admin_bp
    from app.routes.tenant_routes import tenant_bp
    from app.routes.user_routes import user_bp
    from app.routes.test_routes import test_bp
    from app.routes.employee_routes import employee_bp
    from app.routes.access_control_routes import access_control_bp
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(tenant_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(access_control_bp)
    
    # Health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'Multi-tenant SaaS API is running'}, 200
    
    @app.route('/', methods=['GET'])
    def home():
        return {
            'message': 'Welcome to Multi-tenant SaaS Platform API',
            'version': '1.0.0',
            'endpoints': {
                'admin': '/api/admin',
                'tenant': '/api/tenant',
                'user': '/api/user',
                'test': '/api/test'
            }
        }, 200
    
    return app

