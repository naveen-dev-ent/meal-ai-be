"""
Database setup and management script.
Moved from create_db.py for better organization.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.database import Base, engine, init_db
from app.core.config import settings
from app.models.user import *  # Import all models
from app.models.address import *
from app.models.health import *
from app.models.cuisine import *
from app.models.preferences import *
from app.models.pets import *
from app.models.festival import *

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables."""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False


def drop_tables():
    """Drop all database tables."""
    try:
        logger.info("Dropping database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Database tables dropped successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        return False


def reset_database():
    """Reset database by dropping and recreating tables."""
    logger.info("🔄 Resetting database...")
    if drop_tables() and create_tables():
        logger.info("✅ Database reset completed!")
        return True
    else:
        logger.error("❌ Database reset failed!")
        return False


def validate_schema():
    """Validate database schema and models."""
    try:
        logger.info("Validating database schema...")
        
        # Check if all expected tables exist
        expected_tables = [
            "users", "families", "addresses", "user_addresses",
            "health_conditions", "user_health_conditions",
            "cuisines", "user_cuisines", "meal_styles", "user_meal_styles",
            "pets", "festivals", "user_festival_preferences"
        ]
        
        inspector = create_engine(settings.DATABASE_URL).connect()
        existing_tables = inspector.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        existing_table_names = [table[0] for table in existing_tables]
        
        missing_tables = [table for table in expected_tables if table not in existing_table_names]
        
        if missing_tables:
            logger.warning(f"⚠️  Missing tables: {missing_tables}")
        else:
            logger.info("✅ All expected tables exist!")
        
        logger.info(f"📊 Total tables: {len(existing_table_names)}")
        inspector.close()
        
        return len(missing_tables) == 0
        
    except Exception as e:
        logger.error(f"❌ Schema validation failed: {e}")
        return False


async def init_database():
    """Initialize database with async support."""
    try:
        logger.info("Initializing database with async support...")
        await init_db()
        logger.info("✅ Async database initialization completed!")
        return True
    except Exception as e:
        logger.error(f"❌ Async database initialization failed: {e}")
        return False


def main():
    """Main database management function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management script")
    parser.add_argument("--create", action="store_true", help="Create database tables")
    parser.add_argument("--drop", action="store_true", help="Drop database tables")
    parser.add_argument("--reset", action="store_true", help="Reset database (drop and create)")
    parser.add_argument("--validate", action="store_true", help="Validate database schema")
    parser.add_argument("--init", action="store_true", help="Initialize database with async support")
    
    args = parser.parse_args()
    
    if args.create:
        create_tables()
    elif args.drop:
        drop_tables()
    elif args.reset:
        reset_database()
    elif args.validate:
        validate_schema()
    elif args.init:
        asyncio.run(init_database())
    else:
        logger.info("Available commands:")
        logger.info("  --create    Create database tables")
        logger.info("  --drop      Drop database tables")
        logger.info("  --reset     Reset database (drop and create)")
        logger.info("  --validate  Validate database schema")
        logger.info("  --init      Initialize database with async support")


if __name__ == "__main__":
    main()
