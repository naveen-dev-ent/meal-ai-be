import asyncio
import logging
from app.core.database import init_db, close_db, check_db_health

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_database():
    logger.info("🔍 Testing database connection...")
    try:
        # Test database connection
        await init_db()
        logger.info("✅ Database connection successful!")
        
        # Test database health check
        health = await check_db_health()
        logger.info(f"📊 Database health check: {health}")
        
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}", exc_info=True)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(test_database())
