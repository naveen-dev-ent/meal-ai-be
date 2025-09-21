"""
Environment-specific configuration settings.
"""

import os
from pathlib import Path
from typing import Dict, Any


class EnvironmentConfig:
    """Environment-specific configuration management"""
    
    def __init__(self):
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
        self.backend_root = Path(__file__).parent.parent
        
        # Security
        self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # CORS
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:19006")
        
        # Debug
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        
        # SSL
        self.SSL_ENABLED = os.getenv("SSL_ENABLED", "false").lower() == "true"
        self.SSL_CERT_FILE = os.getenv("SSL_CERT_FILE")
        self.SSL_KEY_FILE = os.getenv("SSL_KEY_FILE")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration for current environment"""
        configs = {
            "development": {
                "url": f"sqlite:///{self.backend_root}/data/dev.db",
                "echo": True,
                "pool_pre_ping": True
            },
            "testing": {
                "url": "sqlite:///:memory:",
                "echo": False,
                "pool_pre_ping": False
            },
            "production": {
                "url": os.getenv("DATABASE_URL", f"sqlite:///{self.backend_root}/data/prod.db"),
                "echo": False,
                "pool_pre_ping": True
            }
        }
        return configs.get(self.ENVIRONMENT, configs["development"])
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration for current environment"""
        configs = {
            "development": {
                "allow_origins": [
                    "http://localhost:3000",
                    "http://localhost:19006",
                    "http://localhost:19000"
                ],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"]
            },
            "production": {
                "allow_origins": os.getenv("ALLOWED_ORIGINS", "").split(","),
                "allow_credentials": True,
                "allow_methods": ["GET", "POST", "PUT", "DELETE"],
                "allow_headers": ["*"]
            }
        }
        return configs.get(self.ENVIRONMENT, configs["development"])
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "secret_key": self.SECRET_KEY,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            "ssl_enabled": self.SSL_ENABLED
        }


# Global environment config instance
env_config = EnvironmentConfig()