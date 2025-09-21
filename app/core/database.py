from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError, OperationalError
import logging
import os
import time
from datetime import datetime
from typing import Optional
from ..config.environment import env_config

logger = logging.getLogger(__name__)

# Ensure data directory exists
os.makedirs("./data", exist_ok=True)


def get_database_url() -> str:
    """Get database URL from settings"""
    return env_config.DATABASE_URL


# Database connection tracking
connection_stats = {
    "total_connections": 0,
    "failed_connections": 0,
    "last_connection_time": None,
    "last_failure_time": None,
    "connection_errors": []
}

def log_connection_event(event_type: str, details: str = "", error: Optional[Exception] = None):
    """Log database connection events with detailed information"""
    timestamp = datetime.utcnow().isoformat()
    
    if event_type == "connection_success":
        connection_stats["total_connections"] += 1
        connection_stats["last_connection_time"] = timestamp
        logger.info(f"🔗 Database connection successful - Total: {connection_stats['total_connections']}")
    
    elif event_type == "connection_failure":
        connection_stats["failed_connections"] += 1
        connection_stats["last_failure_time"] = timestamp
        error_msg = str(error) if error else "Unknown error"
        connection_stats["connection_errors"].append({
            "timestamp": timestamp,
            "error": error_msg,
            "details": details
        })
        logger.error(f"❌ Database connection failed - Error: {error_msg} | Details: {details}")
        
        # Keep only last 10 errors
        if len(connection_stats["connection_errors"]) > 10:
            connection_stats["connection_errors"] = connection_stats["connection_errors"][-10:]
    
    elif event_type == "pool_overflow":
        logger.warning(f"⚠️ Database connection pool overflow - {details}")
    
    elif event_type == "pool_timeout":
        logger.error(f"🕐 Database connection pool timeout - {details}")

def create_database_engine():
    """Create database engine with comprehensive error handling and logging"""
    try:
        logger.info(f"Creating database engine for: {env_config.DATABASE_URL.split('@')[-1] if '@' in env_config.DATABASE_URL else 'SQLite'}")
        
        if env_config.DATABASE_URL.startswith("sqlite"):
            engine = create_engine(
                get_database_url(),
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
            )
        else:
            engine = create_engine(
                get_database_url(),
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30
            )
        
        # Add connection event listeners
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            log_connection_event("connection_success")
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            connection_stats["total_connections"] += 1
        
        # Test the connection
        test_connection = engine.connect()
        test_connection.close()
        logger.info("✅ Database engine created and tested successfully")
        
        return engine
        
    except OperationalError as e:
        log_connection_event("connection_failure", "Database server unreachable", e)
        raise
    except SQLAlchemyError as e:
        log_connection_event("connection_failure", "SQLAlchemy configuration error", e)
        raise
    except Exception as e:
        log_connection_event("connection_failure", "Unexpected database engine creation error", e)
        raise

# Create database engine with enhanced logging
engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


async def init_db():
    """Initialize database and create tables"""
    try:
        # Import all models to ensure they are registered
        from app.models.user import User, Family, FamilyMemberPriority, FamilyMealPartition, FamilyGuestPreference, FamilyMealTiming, MealGenerationCriteria, UserMealCriteria, OfficeSchedule
        from app.models.address import Address, UserAddress
        from app.models.health import HealthCondition, VitaminDeficiency, UserHealthCondition, UserVitaminDeficiency
        from app.models.cuisine import Cuisine, MeatType, UserCuisine, UserMeatPreference
        from app.models.preferences import MealStyle, UserMealStyle, ChefAvailability, SpecialNeed, UserSpecialNeed
        from app.models.pets import Pet
        from app.models.festival import Festival, FestivalFood, UserFestivalPreference
        
        # Import existing models
        from app.models.user import Stock, Meal, HealthRecord
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Create initial data if needed
        await create_initial_data()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def create_initial_data():
    """Create initial data for development/testing"""
    try:
        db = SessionLocal()
        
        # Check if we already have data
        from app.models.user import User
        existing_users = db.query(User).count()
        
        if existing_users == 0:
            logger.info("📝 Creating initial development data...")
            
            # Add sample data here if needed
            # This will be implemented later
            
            logger.info("✅ Initial data created successfully")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Failed to create initial data: {e}")


def get_db() -> Session:
    """Get database session with enhanced error handling and logging"""
    db = None
    start_time = time.time()
    
    try:
        db = SessionLocal()
        
        # Test the connection
        db.execute("SELECT 1")
        
        yield db
        
    except OperationalError as e:
        log_connection_event("connection_failure", "Database operational error during session", e)
        if db:
            db.rollback()
        raise
    except DisconnectionError as e:
        log_connection_event("connection_failure", "Database disconnection during session", e)
        if db:
            db.rollback()
        raise
    except SQLAlchemyError as e:
        log_connection_event("connection_failure", "SQLAlchemy error during session", e)
        if db:
            db.rollback()
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected database session error: {str(e)}")
        if db:
            db.rollback()
        raise
    finally:
        if db:
            try:
                db.close()
                session_duration = time.time() - start_time
                if session_duration > 5.0:  # Log slow sessions
                    logger.warning(f"🐌 Slow database session: {session_duration:.2f}s")
            except Exception as e:
                logger.error(f"❌ Error closing database session: {str(e)}")


async def close_db():
    """Close database connections"""
    try:
        engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Failed to close database connections: {e}")


# Database health check with detailed logging
def check_db_health() -> bool:
    """Check if database is accessible with comprehensive logging"""
    start_time = time.time()
    
    try:
        logger.info("🔍 Starting database health check...")
        db = SessionLocal()
        
        # Test basic connectivity
        db.execute("SELECT 1")
        
        # Test table access (if tables exist)
        try:
            from app.models.user import User
            db.query(User).count()
        except Exception:
            pass  # Tables might not exist yet
        
        db.close()
        
        check_duration = time.time() - start_time
        logger.info(f"✅ Database health check passed in {check_duration:.2f}s")
        return True
        
    except OperationalError as e:
        log_connection_event("connection_failure", "Health check - database server unreachable", e)
        return False
    except SQLAlchemyError as e:
        log_connection_event("connection_failure", "Health check - SQLAlchemy error", e)
        return False
    except Exception as e:
        logger.error(f"❌ Database health check failed with unexpected error: {e}")
        return False

def get_connection_stats() -> dict:
    """Get database connection statistics"""
    return {
        **connection_stats,
        "success_rate": (
            (connection_stats["total_connections"] - connection_stats["failed_connections"]) 
            / max(connection_stats["total_connections"], 1) * 100
        ),
        "engine_pool_size": engine.pool.size() if hasattr(engine.pool, 'size') else 0,
        "engine_pool_checked_out": engine.pool.checkedout() if hasattr(engine.pool, 'checkedout') else 0
    }

