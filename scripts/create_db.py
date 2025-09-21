#!/usr/bin/env python3
"""
Database initialization script for normalized schema
Creates all tables for the Money-Health application
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.core.database import Base, get_database_url
from app.models.user import User, Family, FamilyMealTiming, MealGenerationCriteria, UserMealCriteria, OfficeSchedule
from app.models.address import Address, UserAddress
from app.models.health import HealthCondition, VitaminDeficiency, UserHealthCondition, UserVitaminDeficiency
from app.models.cuisine import Cuisine, MeatType, UserCuisine, UserMeatPreference
from app.models.preferences import MealStyle, UserMealStyle, ChefAvailability, SpecialNeed, UserSpecialNeed
from app.models.pets import Pet
from app.models.festival import Festival, FestivalFood, UserFestivalPreference

def create_tables():
    """Create all database tables"""
    try:
        # Get database URL from environment
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        print("Creating all database tables...")
        
        # Verify all models are properly imported and registered
        model_classes = [
            User, Family, FamilyMealTiming, MealGenerationCriteria, UserMealCriteria, OfficeSchedule,
            Address, UserAddress,
            HealthCondition, VitaminDeficiency, UserHealthCondition, UserVitaminDeficiency,
            Cuisine, MeatType, UserCuisine, UserMeatPreference,
            MealStyle, UserMealStyle, ChefAvailability, SpecialNeed, UserSpecialNeed,
            Pet,
            Festival, FestivalFood, UserFestivalPreference
        ]
        
        print(f"Registering {len(model_classes)} model classes...")
        for model in model_classes:
            print(f"  ✓ {model.__tablename__} ({model.__name__})")
        
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Print created tables with model mapping
        print(f"\nCreated {len(Base.metadata.tables)} tables:")
        for table_name in sorted(Base.metadata.tables.keys()):
            # Find corresponding model class
            model_name = next((cls.__name__ for cls in model_classes if cls.__tablename__ == table_name), "Unknown")
            print(f"  - {table_name} ({model_name})")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

def validate_schema():
    """Validate database schema and relationships"""
    try:
        # Group models by category for validation
        user_models = [User, Family, FamilyMealTiming, MealGenerationCriteria, UserMealCriteria, OfficeSchedule]
        address_models = [Address, UserAddress]
        health_models = [HealthCondition, VitaminDeficiency, UserHealthCondition, UserVitaminDeficiency]
        cuisine_models = [Cuisine, MeatType, UserCuisine, UserMeatPreference]
        preference_models = [MealStyle, UserMealStyle, ChefAvailability, SpecialNeed, UserSpecialNeed]
        pet_models = [Pet]
        festival_models = [Festival, FestivalFood, UserFestivalPreference]
        
        all_models = user_models + address_models + health_models + cuisine_models + preference_models + pet_models + festival_models
        
        print("🔍 Validating database schema...")
        print(f"Total models: {len(all_models)}")
        print(f"  - User & Family: {len(user_models)} models")
        print(f"  - Address: {len(address_models)} models")
        print(f"  - Health: {len(health_models)} models")
        print(f"  - Cuisine: {len(cuisine_models)} models")
        print(f"  - Preferences: {len(preference_models)} models")
        print(f"  - Pets: {len(pet_models)} models")
        print(f"  - Festivals: {len(festival_models)} models")
        
        # Validate each model has required attributes
        for model in all_models:
            if not hasattr(model, '__tablename__'):
                print(f"❌ {model.__name__} missing __tablename__")
                return False
            if not hasattr(model, '__table__'):
                print(f"❌ {model.__name__} missing __table__")
                return False
        
        print("✅ Schema validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def drop_tables():
    """Drop all database tables (use with caution!)"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        print("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully!")
        
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management script for Money-Health app")
    parser.add_argument("--drop", action="store_true", help="Drop all tables before creating")
    parser.add_argument("--create", action="store_true", help="Create all tables")
    parser.add_argument("--validate", action="store_true", help="Validate database schema")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables")
    
    args = parser.parse_args()
    
    # Validate schema first if requested
    if args.validate:
        if not validate_schema():
            sys.exit(1)
    
    # Handle reset operation (drop + create)
    if args.reset:
        print("🔄 Resetting database (drop + create)...")
        if drop_tables() and create_tables():
            print("✅ Database reset completed successfully!")
        else:
            print("❌ Database reset failed!")
            sys.exit(1)
    else:
        # Handle individual operations
        if args.drop:
            if not drop_tables():
                sys.exit(1)
        
        if args.create or not any([args.drop, args.validate, args.reset]):
            # Default action is create if no specific action given
            if not validate_schema():
                print("⚠️  Schema validation failed, but proceeding with table creation...")
            
            if not create_tables():
                sys.exit(1)
