
import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ProductionConfig:
    """Production environment configuration"""
    
    # Environment
    environment: str = os.environ.get('ENVIRONMENT', 'development')
    debug_mode: bool = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    # Security
    secret_key: str = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    allowed_hosts: list = field(default_factory=lambda: os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,*.replit.dev,*.replit.co').split(','))
    
    # Database
    database_url: Optional[str] = os.environ.get('DATABASE_URL')
    redis_url: Optional[str] = os.environ.get('REDIS_URL')
    
    # API Limits (Production)
    max_requests_per_minute: int = int(os.environ.get('MAX_REQUESTS_PER_MINUTE', '60'))
    max_concurrent_users: int = int(os.environ.get('MAX_CONCURRENT_USERS', '100'))
    
    # Monitoring
    enable_analytics: bool = os.environ.get('ENABLE_ANALYTICS', 'true').lower() == 'true'
    log_level: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # External Services
    sentry_dsn: Optional[str] = os.environ.get('SENTRY_DSN')
    analytics_key: Optional[str] = os.environ.get('ANALYTICS_KEY')
    
    def is_production(self) -> bool:
        return self.environment.lower() == 'production'
    
    def is_development(self) -> bool:
        return self.environment.lower() == 'development'
    
    def validate_production_readiness(self) -> dict:
        """Validate if configuration is ready for production"""
        issues = []
        
        if self.is_production():
            if self.secret_key == 'dev-key-change-in-production':
                issues.append("SECRET_KEY must be changed for production")
            
            if not self.database_url:
                issues.append("DATABASE_URL required for production")
            
            if self.debug_mode:
                issues.append("DEBUG mode should be disabled in production")
        
        return {
            "ready": len(issues) == 0,
            "issues": issues,
            "environment": self.environment
        }

# Global production config
prod_config = ProductionConfig()
