"""Application settings"""

from app.config.environment import env_config

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL = env_config.DATABASE_URL
    
    # Security
    SECRET_KEY = env_config.SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES = env_config.ACCESS_TOKEN_EXPIRE_MINUTES
    
    # CORS
    CORS_ORIGINS = env_config.CORS_ORIGINS
    
    # Environment
    ENVIRONMENT = env_config.ENVIRONMENT
    DEBUG = env_config.DEBUG
    
    # SSL
    SSL_ENABLED = env_config.SSL_ENABLED
    SSL_CERT_FILE = env_config.SSL_CERT_FILE
    SSL_KEY_FILE = env_config.SSL_KEY_FILE

settings = Settings()