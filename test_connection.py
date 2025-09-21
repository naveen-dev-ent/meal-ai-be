import asyncio
import sys
import os
import logging
from pathlib import Path

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.absolute()
src_dir = backend_dir / 'src'
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(src_dir))

# Log Python path and important directories
logger.info(f"Python path: {sys.path}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Backend directory: {backend_dir}")
logger.info(f"Source directory: {src_dir}")

try:
    # Now import from the src package
    from app.core.database import init_db, close_db, check_db_health
    logger.info("Successfully imported database modules")
except ImportError as e:
    logger.error(f"Failed to import database modules: {e}")
    import traceback
    logger.error(traceback.format_exc())
    raise

async def test_connection():
    print("Testing database connection...")
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialized successfully!")
        
        # Check database health
        health = await check_db_health()
        print(f"📊 Database health: {health}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(test_connection())
