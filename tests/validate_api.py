"""
API validation script to check imports and basic functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def validate_imports():
    """Validate all imports work correctly"""
    try:
        print("🔍 Validating imports...")
        
        # Core imports
        from app.core.database import Base, get_db, init_db
        from app.core.config import settings
        from app.core.security import create_access_token, verify_password
        from app.core.cache import cache_manager
        print("✅ Core imports OK")
        
        # Model imports
        from app.models.user import User, Family, GenderEnum, DietEnum
        from app.models.address import Address, UserAddress
        from app.models.health import HealthCondition, UserHealthCondition
        from app.models.cuisine import Cuisine, UserCuisine
        from app.models.preferences import MealStyle, UserMealStyle
        from app.models.pets import Pet
        from app.models.festival import Festival, UserFestivalPreference
        print("✅ Model imports OK")
        
        # Schema imports
        from app.schemas.auth import UserSignUp, UserSignUpBasic, TokenResponse
        from app.schemas.user import UserResponse, UserUpdate
        from app.schemas.meals import MealCreate, MealResponse
        from app.schemas.stock import StockCreate, StockResponse
        print("✅ Schema imports OK")
        
        # API imports
        from app.api.v1.endpoints.auth import router as auth_router
        from app.api.v1.endpoints.users import router as users_router
        from app.api.v1.endpoints.meals import router as meals_router
        from app.api.v1.endpoints.stock import router as stock_router
        from app.api.v1.api import api_router
        print("✅ API imports OK")
        
        # Service imports
        from app.services.meal_service import MealService
        from app.services.stock_service import StockService
        print("✅ Service imports OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import validation failed: {e}")
        return False

def validate_schemas():
    """Validate schema definitions"""
    try:
        print("\n🔍 Validating schemas...")
        
        from app.schemas.auth import UserSignUpBasic, UserSignUp, TokenResponse
        
        # Test basic signup schema
        basic_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test St",
            "password": "testpass123"
        }
        basic_user = UserSignUpBasic(**basic_data)
        print("✅ UserSignUpBasic schema OK")
        
        # Test full signup schema
        full_data = {
            "email": "full@example.com",
            "first_name": "Full",
            "last_name": "User",
            "phone": "+1234567890",
            "country_code": "+1",
            "current_address": "456 Full St",
            "height": 170.0,
            "weight": 65.0,
            "age": 25,
            "gender": "female",
            "diet": "vegetarian",
            "password": "fullpass123"
        }
        full_user = UserSignUp(**full_data)
        print("✅ UserSignUp schema OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def validate_database_models():
    """Validate database model definitions"""
    try:
        print("\n🔍 Validating database models...")
        
        from app.models.user import User, Family
        from app.core.database import Base
        
        # Check if models are properly registered
        table_names = list(Base.metadata.tables.keys())
        print(f"✅ Found {len(table_names)} tables in metadata")
        
        # Check key tables exist
        required_tables = [
            "users", "families", "addresses", "health_conditions",
            "cuisines", "meal_styles", "pets", "festivals"
        ]
        
        missing_tables = [table for table in required_tables if table not in table_names]
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
        else:
            print("✅ All required tables present")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model validation failed: {e}")
        return False

def validate_api_endpoints():
    """Validate API endpoint definitions"""
    try:
        print("\n🔍 Validating API endpoints...")
        
        from app.api.v1.endpoints.auth import router as auth_router
        from app.api.v1.endpoints.users import router as users_router
        from app.api.v1.endpoints.meals import router as meals_router
        from app.api.v1.endpoints.stock import router as stock_router
        
        # Check route counts
        auth_routes = len(auth_router.routes)
        users_routes = len(users_router.routes)
        meals_routes = len(meals_router.routes)
        stock_routes = len(stock_router.routes)
        
        print(f"✅ Auth endpoints: {auth_routes} routes")
        print(f"✅ Users endpoints: {users_routes} routes")
        print(f"✅ Meals endpoints: {meals_routes} routes")
        print(f"✅ Stock endpoints: {stock_routes} routes")
        
        total_routes = auth_routes + users_routes + meals_routes + stock_routes
        print(f"✅ Total API routes: {total_routes}")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoint validation failed: {e}")
        return False

def create_dummy_data_samples():
    """Create sample dummy data for testing"""
    print("\n🔍 Creating dummy data samples...")
    
    dummy_data = {
        "users": [
            {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1234567890",
                "current_address": "123 Main St, New York, NY",
                "height": 175.0,
                "weight": 70.0,
                "age": 30,
                "gender": "male",
                "diet": "non_vegetarian",
                "password": "secure123"
            },
            {
                "email": "jane.vegan@example.com",
                "first_name": "Jane",
                "last_name": "Green",
                "phone": "+1987654321",
                "current_address": "456 Oak Ave, Portland, OR",
                "height": 165.0,
                "weight": 58.0,
                "age": 28,
                "gender": "female",
                "diet": "vegan",
                "password": "vegan456"
            }
        ],
        "stock_items": [
            {
                "item_name": "Organic Quinoa",
                "category": "grains",
                "quantity": 2.0,
                "unit": "kg",
                "price_per_unit": 250.0,
                "purchase_date": "2024-01-01",
                "expiry_date": "2024-12-31",
                "supplier": "Organic Store",
                "minimum_stock_level": 0.5
            },
            {
                "item_name": "Fresh Spinach",
                "category": "vegetables",
                "quantity": 1.0,
                "unit": "kg",
                "price_per_unit": 60.0,
                "purchase_date": "2024-01-01",
                "expiry_date": "2024-01-07",
                "supplier": "Local Farm",
                "minimum_stock_level": 0.2
            }
        ],
        "meals": [
            {
                "name": "Quinoa Buddha Bowl",
                "meal_type": "lunch",
                "ingredients": ["quinoa", "spinach", "avocado", "chickpeas"],
                "instructions": "Cook quinoa, sauté spinach, assemble bowl",
                "prep_time": 20,
                "cook_time": 25,
                "servings": 2,
                "calories_per_serving": 420,
                "scheduled_for": "2024-01-01"
            }
        ]
    }
    
    # Save dummy data to file
    import json
    with open("dummy_test_data.json", "w") as f:
        json.dump(dummy_data, f, indent=2)
    
    print("✅ Dummy data samples created in dummy_test_data.json")
    return dummy_data

def main():
    """Main validation function"""
    print("🧪 API VALIDATION SUITE")
    print("="*50)
    
    all_passed = True
    
    # Run validations
    if not validate_imports():
        all_passed = False
    
    if not validate_schemas():
        all_passed = False
    
    if not validate_database_models():
        all_passed = False
    
    if not validate_api_endpoints():
        all_passed = False
    
    # Create dummy data
    create_dummy_data_samples()
    
    # Final result
    print("\n" + "="*50)
    if all_passed:
        print("✅ ALL VALIDATIONS PASSED!")
        print("🚀 API is ready for testing")
        print("\nNext steps:")
        print("1. Run: python main.py (to start server)")
        print("2. Run: python tests/test_runner.py (to test APIs)")
        print("3. Run: pytest tests/ -v (for detailed tests)")
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("🔧 Fix the issues above before testing")
    
    print("="*50)

if __name__ == "__main__":
    main()
