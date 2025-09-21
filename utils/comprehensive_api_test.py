"""
Comprehensive API testing with FastAPI TestClient
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import json
from datetime import date

def test_api_endpoints():
    """Test all API endpoints using FastAPI TestClient"""
    
    try:
        # Import the FastAPI app
        from main import app
        from app.core.database import get_db, Base
        
        # Create test database
        SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()
        
        app.dependency_overrides[get_db] = override_get_db
        
        # Create test client
        client = TestClient(app)
        
        print("🧪 COMPREHENSIVE API TESTING")
        print("=" * 50)
        
        results = {}
        
        # Test 1: Basic signup
        print("\n🔐 Testing Authentication Endpoints...")
        signup_data = {
            "email": "apitest@example.com",
            "first_name": "API",
            "last_name": "Tester",
            "address": "123 API Street, Test City",
            "password": "apitest123"
        }
        
        response = client.post("/api/v1/auth/signup", json=signup_data)
        results["basic_signup"] = {
            "status": response.status_code,
            "success": response.status_code == 201,
            "response": response.json() if response.status_code == 201 else response.text
        }
        print(f"✅ Basic Signup: {response.status_code}")
        
        # Get auth token if signup successful
        auth_token = None
        user_id = None
        if response.status_code == 201:
            auth_token = response.json()["access_token"]
            user_id = response.json()["user"]["id"]
        
        # Test 2: Signin
        signin_data = {
            "username": signup_data["email"],
            "password": signup_data["password"]
        }
        response = client.post("/api/v1/auth/signin", data=signin_data)
        results["signin"] = {
            "status": response.status_code,
            "success": response.status_code == 200,
            "response": response.json() if response.status_code == 200 else response.text
        }
        print(f"✅ Signin: {response.status_code}")
        
        # Test 3: Profile completion (if we have auth token)
        if auth_token:
            profile_data = {
                "phone": "+1987654321",
                "country_code": "+1",
                "height": 175.0,
                "weight": 70.0,
                "age": 30,
                "gender": "male",
                "current_postal_code": "12345",
                "current_city": "Test City",
                "current_country": "USA",
                "native_address": "Native Address",
                "native_postal_code": "54321",
                "native_city": "Native City",
                "native_country": "Native Country",
                "diet": "vegetarian",
                "preferred_meats": [],
                "cuisines": ["indian", "italian"],
                "is_family_account": False,
                "family_name": None,
                "is_decision_maker": False
            }
            
            headers = {"Authorization": f"Bearer {auth_token}"}
            response = client.post("/api/v1/auth/complete-profile", json=profile_data, headers=headers)
            results["profile_completion"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"✅ Profile Completion: {response.status_code}")
        
        # Test 4: Stock endpoints
        print("\n📦 Testing Stock Endpoints...")
        if auth_token:
            stock_data = {
                "item_name": "Test Rice",
                "category": "grains",
                "quantity": 5.0,
                "unit": "kg",
                "price_per_unit": 100.0,
                "purchase_date": str(date.today()),
                "expiry_date": "2024-12-31",
                "supplier": "Test Supplier",
                "minimum_stock_level": 1.0
            }
            
            response = client.post("/api/v1/stock/", json=stock_data, headers=headers)
            results["create_stock"] = {
                "status": response.status_code,
                "success": response.status_code == 201,
                "response": response.json() if response.status_code == 201 else response.text
            }
            print(f"✅ Create Stock: {response.status_code}")
            
            # Get stock list
            response = client.get("/api/v1/stock/", headers=headers)
            results["get_stock"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"✅ Get Stock List: {response.status_code}")
        
        # Test 5: Meal endpoints
        print("\n🍽️ Testing Meal Endpoints...")
        if auth_token:
            meal_data = {
                "name": "Test Meal",
                "meal_type": "lunch",
                "ingredients": ["rice", "vegetables"],
                "instructions": "Cook rice with vegetables",
                "prep_time": 15,
                "cook_time": 30,
                "servings": 4,
                "calories_per_serving": 300,
                "scheduled_for": str(date.today())
            }
            
            response = client.post("/api/v1/meals/", json=meal_data, headers=headers)
            results["create_meal"] = {
                "status": response.status_code,
                "success": response.status_code == 201,
                "response": response.json() if response.status_code == 201 else response.text
            }
            print(f"✅ Create Meal: {response.status_code}")
            
            # Get meals list
            response = client.get("/api/v1/meals/", headers=headers)
            results["get_meals"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"✅ Get Meals List: {response.status_code}")
        
        # Test 6: User endpoints
        print("\n👤 Testing User Endpoints...")
        if auth_token:
            response = client.get("/api/v1/users/", headers=headers)
            results["get_users"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "response": response.json() if response.status_code == 200 else response.text
            }
            print(f"✅ Get Users List: {response.status_code}")
            
            if user_id:
                response = client.get(f"/api/v1/users/{user_id}", headers=headers)
                results["get_user_by_id"] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "response": response.json() if response.status_code == 200 else response.text
                }
                print(f"✅ Get User by ID: {response.status_code}")
        
        # Summary
        print(f"\n📊 TEST SUMMARY")
        print("=" * 30)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result.get("success"))
        
        for test_name, result in results.items():
            status = "✅" if result.get("success") else "❌"
            print(f"{status} {test_name}: {result.get('status', 'unknown')}")
        
        print(f"\n🎯 RESULTS: {passed_tests}/{total_tests} tests passed")
        
        # Save detailed results
        with open("api_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Detailed results saved to api_test_results.json")
        
        if passed_tests == total_tests:
            print("🚀 ALL API TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed - check results above")
            return False
        
    except Exception as e:
        print(f"❌ API testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🧪 Starting comprehensive API testing...")
    
    success = test_api_endpoints()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ API TESTING COMPLETED SUCCESSFULLY!")
        print("🎉 All endpoints are functional")
    else:
        print("❌ API TESTING COMPLETED WITH ISSUES")
        print("🔧 Check the errors above for details")
    print("=" * 50)

if __name__ == "__main__":
    main()
