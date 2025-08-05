
#!/usr/bin/env python3
"""
Enterprise Deployment Script
Automates production deployment setup and validation
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from production_config import prod_config
from health_check import health_check

def validate_environment():
    """Validate production environment setup"""
    print("🔍 Validating production environment...")
    
    validation = prod_config.validate_production_readiness()
    
    if validation["ready"]:
        print("✅ Production environment validated")
        return True
    else:
        print("❌ Production validation failed:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'streamlit', 'openai', 'anthropic', 'sqlalchemy', 
        'psycopg2-binary', 'pyjwt', 'psutil'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All dependencies satisfied")
    return True

def setup_database():
    """Initialize database tables"""
    print("🗄️ Setting up database...")
    
    try:
        from database import create_tables
        create_tables()
        print("✅ Database tables created")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def run_health_check():
    """Run comprehensive health check"""
    print("🏥 Running health check...")
    
    health = health_check()
    
    if health["status"] == "healthy":
        print("✅ Health check passed")
        return True
    else:
        print(f"❌ Health check failed: {health.get('error', 'Unknown error')}")
        if "issues" in health:
            for issue in health["issues"]:
                print(f"  - {issue}")
        return False

def create_admin_user():
    """Create initial admin user"""
    print("👤 Setting up admin user...")
    
    try:
        from auth_manager import auth_manager
        # Admin user is automatically created during initialization
        print("✅ Admin user ready (username: admin, password: admin123)")
        print("⚠️  IMPORTANT: Change the admin password after first login!")
        return True
    except Exception as e:
        print(f"❌ Admin setup failed: {e}")
        return False

def deploy():
    """Main deployment function"""
    print("🚀 Starting enterprise deployment...")
    print(f"📅 Deployment time: {datetime.now().isoformat()}")
    print(f"🌍 Environment: {prod_config.environment}")
    
    steps = [
        ("Environment Validation", validate_environment),
        ("Dependencies Check", check_dependencies),
        ("Database Setup", setup_database),
        ("Admin User Setup", create_admin_user),
        ("Health Check", run_health_check)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        if not step_func():
            print(f"💥 Deployment failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Enterprise deployment completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Set your environment variables in production")
    print("2. Change the default admin password")
    print("3. Configure your email notifications")
    print("4. Set up your usage limits")
    print("5. Test all features with your team")
    
    print(f"\n🌐 Your app is ready at: http://0.0.0.0:5000")

if __name__ == "__main__":
    deploy()
