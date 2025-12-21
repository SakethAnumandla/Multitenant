# Import all route blueprints
from app.routes.admin_routes import admin_bp
from app.routes.tenant_routes import tenant_bp
from app.routes.user_routes import user_bp
from app.routes.test_routes import test_bp

__all__ = ['admin_bp', 'tenant_bp', 'user_bp', 'test_bp']

