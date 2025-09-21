"""
Scripts package for backend utilities and tools.

This package contains essential scripts for:
- Database setup and management
- Application startup and initialization
- Environment validation and configuration
"""

from .database_setup import (
    create_tables,
    drop_tables,
    reset_database,
    validate_schema,
    init_database
)

from .startup import (
    check_environment,
    setup_database,
    start_application
)

# Version info
__version__ = "1.0.0"

# Expose main functions for easy import
__all__ = [
    # Database management
    "create_tables",
    "drop_tables", 
    "reset_database",
    "validate_schema",
    "init_database",
    
    # Application startup
    "check_environment",
    "setup_database", 
    "start_application",
    
    # Version
    "__version__"
]

# Quick access functions
def quick_setup():
    """Quick database setup for development"""
    print("🚀 Quick Setup - Creating database tables...")
    return create_tables()

def quick_reset():
    """Quick database reset for development"""
    print("🔄 Quick Reset - Resetting database...")
    return reset_database()

def quick_validate():
    """Quick validation check"""
    print("✅ Quick Validate - Checking database schema...")
    return validate_schema()

# Add quick functions to exports
__all__.extend(["quick_setup", "quick_reset", "quick_validate"])
