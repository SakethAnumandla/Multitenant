from app import create_app
from app.config import Config

# Create Flask application
app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Multi-tenant SaaS Platform API")
    print("=" * 50)
    print(f"📍 Running on: http://{Config.APP_HOST}:{Config.APP_PORT}")
    print(f"🔧 Debug Mode: {Config.DEBUG}")
    print(f"📊 Database: {Config.DATABASE_NAME}")
    print("=" * 50)
    
    app.run(
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        debug=Config.DEBUG
    )

