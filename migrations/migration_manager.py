"""
Database migration management utilities.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, MetaData
from app.core.config import settings
from app.core.database import Base
from config.logging_config import logger


class MigrationManager:
    """Manage database migrations and schema changes"""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.metadata = MetaData()
        self.migrations_dir = Path(__file__).parent
        
    def create_migration(self, name: str, description: str = "") -> str:
        """Create a new migration file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name.lower().replace(' ', '_')}.py"
        filepath = self.migrations_dir / filename
        
        migration_template = f'''"""
Migration: {name}
Created: {datetime.now().isoformat()}
Description: {description}
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers
revision = '{timestamp}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Apply migration changes"""
    # Add your upgrade logic here
    pass


def downgrade():
    """Revert migration changes"""
    # Add your downgrade logic here
    pass
'''
        
        with open(filepath, 'w') as f:
            f.write(migration_template)
        
        logger.info(f"Created migration: {filename}")
        return str(filepath)
    
    def list_migrations(self) -> List[Dict[str, Any]]:
        """List all available migrations"""
        migrations = []
        
        for file in sorted(self.migrations_dir.glob("*.py")):
            if file.name.startswith("__"):
                continue
                
            try:
                # Extract timestamp and name from filename
                parts = file.stem.split("_", 2)
                if len(parts) >= 2:
                    timestamp = f"{parts[0]}_{parts[1]}"
                    name = parts[2] if len(parts) > 2 else "unnamed"
                    
                    migrations.append({
                        "file": file.name,
                        "timestamp": timestamp,
                        "name": name.replace("_", " ").title(),
                        "path": str(file)
                    })
            except Exception as e:
                logger.warning(f"Could not parse migration file {file.name}: {e}")
        
        return migrations
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get current database schema information"""
        try:
            with self.engine.connect() as conn:
                # Get table names
                tables_result = conn.execute(text(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ))
                tables = [row[0] for row in tables_result]
                
                schema_info = {
                    "total_tables": len(tables),
                    "tables": tables,
                    "expected_tables": list(Base.metadata.tables.keys()),
                    "missing_tables": [],
                    "extra_tables": []
                }
                
                expected_set = set(Base.metadata.tables.keys())
                actual_set = set(tables)
                
                schema_info["missing_tables"] = list(expected_set - actual_set)
                schema_info["extra_tables"] = list(actual_set - expected_set)
                
                return schema_info
                
        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            return {"error": str(e)}
    
    def validate_schema(self) -> bool:
        """Validate current schema against models"""
        schema_info = self.get_schema_info()
        
        if "error" in schema_info:
            return False
        
        missing = schema_info.get("missing_tables", [])
        if missing:
            logger.warning(f"Missing tables: {missing}")
            return False
        
        logger.info("Schema validation passed")
        return True
    
    def backup_database(self) -> str:
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.db"
        backup_path = self.migrations_dir / backup_name
        
        try:
            # For SQLite, copy the database file
            if "sqlite" in settings.DATABASE_URL:
                import shutil
                db_path = settings.DATABASE_URL.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    shutil.copy2(db_path, backup_path)
                    logger.info(f"Database backed up to: {backup_path}")
                    return str(backup_path)
            
            logger.warning("Backup not implemented for this database type")
            return ""
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return ""


def main():
    """Migration manager CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database migration manager")
    parser.add_argument("--create", help="Create new migration")
    parser.add_argument("--list", action="store_true", help="List migrations")
    parser.add_argument("--validate", action="store_true", help="Validate schema")
    parser.add_argument("--backup", action="store_true", help="Backup database")
    parser.add_argument("--info", action="store_true", help="Show schema info")
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.create:
        filepath = manager.create_migration(args.create)
        print(f"Created migration: {filepath}")
    
    elif args.list:
        migrations = manager.list_migrations()
        print(f"\n📋 Available Migrations ({len(migrations)}):")
        for migration in migrations:
            print(f"  {migration['timestamp']} - {migration['name']}")
    
    elif args.validate:
        valid = manager.validate_schema()
        print(f"Schema validation: {'✅ PASSED' if valid else '❌ FAILED'}")
    
    elif args.backup:
        backup_path = manager.backup_database()
        if backup_path:
            print(f"Backup created: {backup_path}")
        else:
            print("Backup failed")
    
    elif args.info:
        info = manager.get_schema_info()
        print(f"\n📊 Schema Information:")
        print(f"  Total tables: {info.get('total_tables', 0)}")
        print(f"  Expected tables: {len(info.get('expected_tables', []))}")
        if info.get('missing_tables'):
            print(f"  Missing tables: {info['missing_tables']}")
        if info.get('extra_tables'):
            print(f"  Extra tables: {info['extra_tables']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
