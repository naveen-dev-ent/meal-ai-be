"""
Environment-specific configuration settings.
"""

import os
from pathlib import Path
from typing import Dict, Any


class EnvironmentConfig:
    """Environment-specific configuration management"""
    
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT", "development")
        self.backend_root = Path(__file__).parent.parent
    
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
        return configs.get(self.env, configs["development"])
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration for current environment"""
        configs = {
            "development": {
                "host": "0.0.0.0",
                "port": 8000,
                "reload": True,
                "debug": True
            },
            "testing": {
                "host": "127.0.0.1",
                "port": 8001,
                "reload": False,
                "debug": False
            },
            "production": {
                "host": "0.0.0.0",
                "port": int(os.getenv("PORT", 8000)),
                "reload": False,
                "debug": False
            }
        }
        return configs.get(self.env, configs["development"])
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration for current environment"""
        return {
            "secret_key": os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
            "algorithm": "HS256",
            "access_token_expire_minutes": 30,
            "refresh_token_expire_days": 7,
            "password_min_length": 8
        }
    
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
        return configs.get(self.env, configs["development"])


# Global environment config instance
env_config = EnvironmentConfig()
