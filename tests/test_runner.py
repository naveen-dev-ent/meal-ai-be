"""
Test runner for all API endpoints with dummy data validation
"""

import sys
import os
import asyncio
import requests
import json
from datetime import date
from typing import Dict, Any

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class APITester:
    """Comprehensive API testing with dummy data"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        
    def test_auth_endpoints(self) -> Dict[str, Any]:
        """Test all authentication endpoints"""
        results = {}
        
        # Test data
        signup_data = {
            "email": "apitest@example.com",
            "first_name": "API",
            "last_name": "Tester",
            "address": "123 API Street, Test City",
            "password": "apitest123"
        }
        
        # 1. Test basic signup
        try:
            response = self.session.post(f"{self.base_url}/api/v1/auth/signup", json=signup_data)
            results["signup_basic"] = {
                "status": response.status_code,
                "success": response.status_code == 201,
                "data": response.json() if response.status_code == 201 else response.text
            }
            
            if response.status_code == 201:
                self.auth_token = response.json()["access_token"]
                self.user_id = response.json()["user"]["id"]
                
        except Exception as e:
            results["signup_basic"] = {"status": "error", "success": False, "error": str(e)}
        
        # 2. Test signin
        try:
            signin_data = {
                "username": signup_data["email"],
                "password": signup_data["password"]
            }
            response = self.session.post(f"{self.base_url}/api/v1/auth/signin", data=signin_data)
            results["signin_form"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results["signin_form"] = {"status": "error", "success": False, "error": str(e)}
        
        # 3. Test JSON signin
        try:
            signin_json = {
                "email_or_phone": signup_data["email"],
                "password": signup_data["password"]
            }
            response = self.session.post(f"{self.base_url}/api/v1/auth/signin-json", json=signin_json)
            results["signin_json"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results["signin_json"] = {"status": "error", "success": False, "error": str(e)}
        
        # 4. Test profile completion
        if self.auth_token:
            try:
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
                
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.session.post(
                    f"{self.base_url}/api/v1/auth/complete-profile",
                    json=profile_data,
                    headers=headers
                )
                results["profile_completion"] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else response.text
                }
            except Exception as e:
                results["profile_completion"] = {"status": "error", "success": False, "error": str(e)}
        
        # 5. Test get profile
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = self.session.get(f"{self.base_url}/api/v1/auth/profile", headers=headers)
                results["get_profile"] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else response.text
                }
            except Exception as e:
                results["get_profile"] = {"status": "error", "success": False, "error": str(e)}
        
        return results
    
    def test_stock_endpoints(self) -> Dict[str, Any]:
        """Test all stock endpoints"""
        results = {}
        
        if not self.auth_token:
            return {"error": "No auth token available"}
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test data
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
        
        # 1. Create stock item
        try:
            response = self.session.post(f"{self.base_url}/api/v1/stock/", json=stock_data, headers=headers)
            results["create_stock"] = {
                "status": response.status_code,
                "success": response.status_code == 201,
                "data": response.json() if response.status_code == 201 else response.text
            }
            
            stock_id = response.json().get("id") if response.status_code == 201 else None
            
        except Exception as e:
            results["create_stock"] = {"status": "error", "success": False, "error": str(e)}
            stock_id = None
        
        # 2. Get stock list
        try:
            response = self.session.get(f"{self.base_url}/api/v1/stock/", headers=headers)
            results["get_stock_list"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results["get_stock_list"] = {"status": "error", "success": False, "error": str(e)}
        
        # 3. Test stock analytics
        try:
            response = self.session.get(f"{self.base_url}/api/v1/stock/analytics", headers=headers)
            results["stock_analytics"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results["stock_analytics"] = {"status": "error", "success": False, "error": str(e)}
        
        return results
    
    def test_meal_endpoints(self) -> Dict[str, Any]:
        """Test all meal endpoints"""
        results = {}
        
        if not self.auth_token:
            return {"error": "No auth token available"}
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test data
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
        
        # 1. Create meal
        try:
            response = self.session.post(f"{self.base_url}/api/v1/meals/", json=meal_data, headers=headers)
            results["create_meal"] = {
                "status": response.status_code,
                "success": response.status_code == 201,
                "data": response.json() if response.status_code == 201 else response.text
            }
        except Exception as e:
            results["create_meal"] = {"status": "error", "success": False, "error": str(e)}
        
        # 2. Get meals list
        try:
            response = self.session.get(f"{self.base_url}/api/v1/meals/", headers=headers)
            results["get_meals_list"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results["get_meals_list"] = {"status": "error", "success": False, "error": str(e)}
        
        # 3. Test meal generation
        try:
            generation_data = {
                "meal_type": "dinner",
                "dietary_preferences": ["vegetarian"],
                "cuisine_preferences": ["indian"],
                "target_date": str(date.today()),
                "servings": 2,
                "budget_limit": 300.0
            }
            response = self.session.post(f"{self.base_url}/api/v1/meals/generate", json=generation_data, headers=headers)
            results["generate_meal"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results["generate_meal"] = {"status": "error", "success": False, "error": str(e)}
        
        return results
    
    def test_user_endpoints(self) -> Dict[str, Any]:
        """Test all user endpoints"""
        results = {}
        
        if not self.auth_token:
            return {"error": "No auth token available"}
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # 1. Get users list
        try:
            response = self.session.get(f"{self.base_url}/api/v1/users/", headers=headers)
            results["get_users_list"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
        except Exception as e:
            results["get_users_list"] = {"status": "error", "success": False, "error": str(e)}
        
        # 2. Get specific user
        if self.user_id:
            try:
                response = self.session.get(f"{self.base_url}/api/v1/users/{self.user_id}", headers=headers)
                results["get_user_by_id"] = {
                    "status": response.status_code,
                    "success": response.status_code == 200,
                    "data": response.json() if response.status_code == 200 else response.text
                }
            except Exception as e:
                results["get_user_by_id"] = {"status": "error", "success": False, "error": str(e)}
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests"""
        print("🧪 Starting comprehensive API testing...")
        
        all_results = {}
        
        # Test authentication endpoints
        print("🔐 Testing authentication endpoints...")
        all_results["auth"] = self.test_auth_endpoints()
        
        # Test stock endpoints
        print("📦 Testing stock endpoints...")
        all_results["stock"] = self.test_stock_endpoints()
        
        # Test meal endpoints
        print("🍽️ Testing meal endpoints...")
        all_results["meals"] = self.test_meal_endpoints()
        
        # Test user endpoints
        print("👤 Testing user endpoints...")
        all_results["users"] = self.test_user_endpoints()
        
        return all_results
    
    def print_results(self, results: Dict[str, Any]):
        """Print formatted test results"""
        print("\n" + "="*60)
        print("🧪 API TEST RESULTS")
        print("="*60)
        
        for category, tests in results.items():
            print(f"\n📋 {category.upper()} ENDPOINTS:")
            print("-" * 40)
            
            if isinstance(tests, dict) and "error" in tests:
                print(f"❌ Category Error: {tests['error']}")
                continue
            
            for test_name, result in tests.items():
                if isinstance(result, dict):
                    status = "✅" if result.get("success") else "❌"
                    print(f"{status} {test_name}: {result.get('status', 'unknown')}")
                    if not result.get("success") and "error" in result:
                        print(f"   Error: {result['error']}")
        
        # Summary
        total_tests = 0
        passed_tests = 0
        
        for category, tests in results.items():
            if isinstance(tests, dict) and "error" not in tests:
                for test_name, result in tests.items():
                    if isinstance(result, dict):
                        total_tests += 1
                        if result.get("success"):
                            passed_tests += 1
        
        print(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
        print("="*60)

def main():
    """Main test runner"""
    tester = APITester()
    
    print("🚀 Starting API functionality tests...")
    print("⚠️  Make sure the backend server is running on http://localhost:8000")
    
    # Check if server is running
    try:
        response = requests.get(f"{tester.base_url}/docs", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server not accessible. Please start the server first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("💡 Run: python main.py")
        return
    
    # Run tests
    results = tester.run_all_tests()
    tester.print_results(results)
    
    # Save results to file
    with open("api_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to api_test_results.json")

if __name__ == "__main__":
    main()
