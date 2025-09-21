"""
Application startup script with environment setup.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.environment import env_config
from config.logging_config import logger
from scripts.database_setup import create_tables, validate_schema


def check_environment():
    """Check environment setup and dependencies"""
    logger.info("🔍 Checking environment setup...")
    
    checks = {
        "database_config": False,
        "api_config": False,
        "security_config": False,
        "directories": False
    }
    
    try:
        # Check database config
        db_config = env_config.get_database_config()
        if db_config.get("url"):
            checks["database_config"] = True
            logger.info(f"✅ Database: {db_config['url']}")
        
        # Check API config
        api_config = env_config.get_api_config()
        if api_config.get("host") and api_config.get("port"):
            checks["api_config"] = True
            logger.info(f"✅ API: {api_config['host']}:{api_config['port']}")
        
        # Check security config
        security_config = env_config.get_security_config()
        if security_config.get("secret_key"):
            checks["security_config"] = True
            logger.info("✅ Security configuration loaded")
        
        # Check required directories
        backend_root = Path(__file__).parent.parent
        required_dirs = ["data", "logs", "uploads"]
        
        for dir_name in required_dirs:
            dir_path = backend_root / dir_name
            dir_path.mkdir(exist_ok=True)
        
        checks["directories"] = True
        logger.info("✅ Required directories created")
        
    except Exception as e:
        logger.error(f"❌ Environment check failed: {e}")
    
    return checks


def setup_database():
    """Setup and validate database"""
    logger.info("🗄️ Setting up database...")
    
    try:
        # Create tables
        if create_tables():
            logger.info("✅ Database tables created")
        
        # Validate schema
        if validate_schema():
            logger.info("✅ Database schema validated")
            return True
        else:
            logger.warning("⚠️ Database schema validation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False


def start_application():
    """Start the FastAPI application"""
    logger.info("🚀 Starting Money-Health Backend API...")
    
    # Environment checks
    env_checks = check_environment()
    if not all(env_checks.values()):
        logger.error("❌ Environment checks failed")
        return False
    
    # Database setup
    if not setup_database():
        logger.error("❌ Database setup failed")
        return False
    
    # Import and start FastAPI app
    try:
        import uvicorn
        from app.main import app
        
        api_config = env_config.get_api_config()
        
        logger.info(f"🌐 Starting server on {api_config['host']}:{api_config['port']}")
        logger.info(f"📚 API Documentation: http://{api_config['host']}:{api_config['port']}/docs")
        
        uvicorn.run(
            "app.main:app",
            host=api_config["host"],
            port=api_config["port"],
            reload=api_config["reload"],
            log_level="info"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        return False


if __name__ == "__main__":
    start_application()
