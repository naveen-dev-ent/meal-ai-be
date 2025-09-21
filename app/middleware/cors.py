"""CORS middleware configuration"""

from fastapi.middleware.cors import CORSMiddleware
from app.config.environment import env_config

def add_cors_middleware(app):
    """Add CORS middleware to FastAPI app"""
    cors_config = env_config.get_cors_config()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
    )