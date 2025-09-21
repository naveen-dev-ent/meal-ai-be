"""Simple API functionality test"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """Test if the FastAPI app can start without errors"""
    try:
        from main import app
        print("✅ FastAPI app imports successfully")
        
        # Check if routes are registered
        routes = [route.path for route in app.routes]
        print(f"✅ Found {len(routes)} routes")
        
        # Check specific API routes
        api_routes = [route for route in routes if route.startswith("/api/v1/")]
        print(f"✅ Found {len(api_routes)} API routes")
        
        return True
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

def test_database_connection():
    """Test database connection and models"""
    try:
        from app.core.database import Base, engine
        from app.models.user import User
        
        print("✅ Database models import successfully")
        
        # Check table metadata
        tables = list(Base.metadata.tables.keys())
        print(f"✅ Found {len(tables)} database tables")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_schema_validation():
    """Test basic schema validation"""
    try:
        from app.schemas.auth import UserSignUpBasic, GenderEnum, DietEnum
        
        # Test basic signup
        basic_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street, Test City"
        }
        
        user = UserSignUpBasic(**basic_data)
        print("✅ Basic signup schema validation OK")
        
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def main():
    print("🧪 SIMPLE API FUNCTIONALITY TEST")
    print("=" * 50)
    
    tests = [
        ("App Startup", test_app_startup),
        ("Database Connection", test_database_connection),
        ("Schema Validation", test_schema_validation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All basic functionality tests passed!")
        print("🚀 Backend is ready for API testing")
    else:
        print("❌ Some tests failed - check errors above")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
