"""
Testing utilities and validation tools.
Consolidated from various test files for better organization.
"""

import sys
import os
import json
import requests
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app
from app.core.database import get_db, Base
from app.schemas.auth import UserSignUpBasic, GenderEnum, DietEnum


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
        
        # Basic signup test
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
        
        return results
    
    def test_stock_endpoints(self) -> Dict[str, Any]:
        """Test all stock endpoints"""
        results = {}
        
        if not self.auth_token:
            return {"error": "No auth token available"}
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
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
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/stock/", json=stock_data, headers=headers)
            results["create_stock"] = {
                "status": response.status_code,
                "success": response.status_code == 201,
                "data": response.json() if response.status_code == 201 else response.text
            }
        except Exception as e:
            results["create_stock"] = {"status": "error", "success": False, "error": str(e)}
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all API tests"""
        all_results = {}
        all_results["auth"] = self.test_auth_endpoints()
        all_results["stock"] = self.test_stock_endpoints()
        return all_results


class SchemaValidator:
    """Validate Pydantic schemas and imports"""
    
    @staticmethod
    def validate_imports():
        """Validate all imports work correctly"""
        try:
            from app.core.database import Base, get_db, init_db
            from app.core.config import settings
            from app.core.security import create_access_token, verify_password
            from app.models.user import User, Family, GenderEnum, DietEnum
            from app.schemas.auth import UserSignUpBasic, UserSignUp, TokenResponse
            return True
        except Exception as e:
            print(f"❌ Import validation failed: {e}")
            return False
    
    @staticmethod
    def validate_schemas():
        """Validate schema definitions"""
        try:
            basic_data = {
                "email": "test@example.com",
                "password": "testpass123",
                "first_name": "Test",
                "last_name": "User",
                "address": "123 Test Street, Test City"
            }
            user = UserSignUpBasic(**basic_data)
            return True
        except Exception as e:
            print(f"❌ Schema validation failed: {e}")
            return False


class DummyDataGenerator:
    """Generate realistic dummy data for testing"""
    
    @staticmethod
    def create_user_data() -> List[Dict[str, Any]]:
        """Create sample user data"""
        return [
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
        ]
    
    @staticmethod
    def create_stock_data() -> List[Dict[str, Any]]:
        """Create sample stock data"""
        return [
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
        ]
    
    @staticmethod
    def create_meal_data() -> List[Dict[str, Any]]:
        """Create sample meal data"""
        return [
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


def run_comprehensive_tests():
    """Run all validation and testing"""
    print("🧪 COMPREHENSIVE BACKEND TESTING")
    print("=" * 50)
    
    # Schema validation
    print("\n🔍 Validating Schemas...")
    validator = SchemaValidator()
    schema_valid = validator.validate_schemas()
    import_valid = validator.validate_imports()
    
    # Generate dummy data
    print("\n📊 Generating Dummy Data...")
    generator = DummyDataGenerator()
    users = generator.create_user_data()
    stock = generator.create_stock_data()
    meals = generator.create_meal_data()
    
    # Save test data
    test_data = {
        "users": users,
        "stock_items": stock,
        "meals": meals
    }
    
    with open("test_data_generated.json", "w") as f:
        json.dump(test_data, f, indent=2)
    
    print(f"✅ Generated {len(users)} users, {len(stock)} stock items, {len(meals)} meals")
    print("💾 Test data saved to test_data_generated.json")
    
    # Summary
    print(f"\n📋 VALIDATION SUMMARY:")
    print(f"{'✅' if schema_valid else '❌'} Schema Validation")
    print(f"{'✅' if import_valid else '❌'} Import Validation")
    print("=" * 50)


if __name__ == "__main__":
    run_comprehensive_tests()
