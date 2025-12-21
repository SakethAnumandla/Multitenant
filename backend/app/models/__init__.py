# Import all models here for easy access
from app.models.admin import Admin
from app.models.tenant import Tenant
from app.models.user import User
from app.models.test import Test, Question, TestResponse
from app.models.access_matrix import AccessMatrix

__all__ = ['Admin', 'Tenant', 'User', 'Test', 'Question', 'TestResponse', 'AccessMatrix']

