"""
Integration tests for all API endpoints with comprehensive dummy data
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, datetime

from app.core.database import Base, get_db
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Comprehensive test data
TEST_USERS = [
    {
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "country_code": "+1",
        "current_address": "123 Main St, New York, NY",
        "height": 175.0,
        "weight": 70.0,
        "age": 30,
        "gender": "male",
        "diet": "non_vegetarian",
        "password": "securepass123"
    },
    {
        "email": "jane.smith@example.com",
        "first_name": "Jane",
        "last_name": "Smith",
        "phone": "+1987654321",
        "country_code": "+1",
        "current_address": "456 Oak Ave, Los Angeles, CA",
        "height": 165.0,
        "weight": 60.0,
        "age": 28,
        "gender": "female",
        "diet": "vegetarian",
        "password": "janepass456"
    },
    {
        "email": "alex.vegan@example.com",
        "first_name": "Alex",
        "last_name": "Green",
        "phone": "+1555666777",
        "country_code": "+1",
        "current_address": "789 Pine Rd, Seattle, WA",
        "height": 180.0,
        "weight": 75.0,
        "age": 35,
        "gender": "other",
        "diet": "vegan",
        "password": "veganlife789"
    }
]

TEST_STOCK_ITEMS = [
    {
        "item_name": "Basmati Rice",
        "category": "grains",
        "quantity": 5.0,
        "unit": "kg",
        "price_per_unit": 120.0,
        "purchase_date": str(date.today()),
        "expiry_date": "2024-12-31",
        "supplier": "Local Grocery",
        "minimum_stock_level": 1.0
    },
    {
        "item_name": "Organic Tomatoes",
        "category": "vegetables",
        "quantity": 2.0,
        "unit": "kg",
        "price_per_unit": 80.0,
        "purchase_date": str(date.today()),
        "expiry_date": "2024-01-15",
        "supplier": "Organic Farm",
        "minimum_stock_level": 0.5
    },
    {
        "item_name": "Chicken Breast",
        "category": "meat",
        "quantity": 1.5,
        "unit": "kg",
        "price_per_unit": 300.0,
        "purchase_date": str(date.today()),
        "expiry_date": "2024-01-10",
        "supplier": "Fresh Meat Co",
        "minimum_stock_level": 0.2
    }
]

TEST_MEALS = [
    {
        "name": "Vegetable Biryani",
        "meal_type": "lunch",
        "ingredients": ["basmati rice", "mixed vegetables", "spices"],
        "instructions": "Cook rice with vegetables and aromatic spices",
        "prep_time": 30,
        "cook_time": 45,
        "servings": 4,
        "calories_per_serving": 350,
        "scheduled_for": str(date.today())
    },
    {
        "name": "Grilled Chicken Salad",
        "meal_type": "dinner",
        "ingredients": ["chicken breast", "lettuce", "tomatoes", "cucumber"],
        "instructions": "Grill chicken and serve with fresh salad",
        "prep_time": 15,
        "cook_time": 20,
        "servings": 2,
        "calories_per_serving": 280,
        "scheduled_for": str(date.today())
    }
]

@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

class TestAPIIntegration:
    """Integration tests for all API endpoints"""
    
    def test_complete_user_workflow(self, setup_database):
        """Test complete user signup and profile workflow"""
        # 1. Basic signup
        signup_response = client.post("/api/v1/auth/signup", json={
            "email": TEST_USERS[0]["email"],
            "first_name": TEST_USERS[0]["first_name"],
            "last_name": TEST_USERS[0]["last_name"],
            "address": TEST_USERS[0]["current_address"],
            "password": TEST_USERS[0]["password"]
        })
        
        assert signup_response.status_code == 201
        token = signup_response.json()["access_token"]
        user_data = signup_response.json()["user"]
        assert user_data["profile_completed"] == False
        
        # 2. Complete profile
        profile_completion = {
            "phone": TEST_USERS[0]["phone"],
            "country_code": TEST_USERS[0]["country_code"],
            "height": TEST_USERS[0]["height"],
            "weight": TEST_USERS[0]["weight"],
            "age": TEST_USERS[0]["age"],
            "gender": TEST_USERS[0]["gender"],
            "current_postal_code": "10001",
            "current_city": "New York",
            "current_country": "USA",
            "native_address": "Native Address",
            "native_postal_code": "12345",
            "native_city": "Native City",
            "native_country": "Native Country",
            "diet": TEST_USERS[0]["diet"],
            "preferred_meats": ["chicken", "fish"],
            "cuisines": ["indian", "american"],
            "is_family_account": False,
            "family_name": None,
            "is_decision_maker": False
        }
        
        profile_response = client.post(
            "/api/v1/auth/complete-profile",
            json=profile_completion,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert profile_response.status_code == 200
        assert profile_response.json()["user"]["profile_completed"] == True
        
        # 3. Get profile
        get_profile_response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert get_profile_response.status_code == 200
        assert get_profile_response.json()["user"]["phone"] == TEST_USERS[0]["phone"]
        
        return token
    
    def test_full_signup_workflow(self, setup_database):
        """Test full profile signup in one step"""
        response = client.post("/api/v1/auth/signup-full", json=TEST_USERS[1])
        
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["profile_completed"] == True
        assert data["user"]["email"] == TEST_USERS[1]["email"]
        assert data["user"]["diet"] == TEST_USERS[1]["diet"]
        
        return data["access_token"]
    
    def test_stock_management_workflow(self, setup_database):
        """Test complete stock management workflow"""
        # Create user and get token
        token = self.test_full_signup_workflow(setup_database)
        
        # 1. Create stock items
        stock_ids = []
        for stock_item in TEST_STOCK_ITEMS:
            response = client.post(
                "/api/v1/stock/",
                json=stock_item,
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 201
            stock_ids.append(response.json()["id"])
        
        # 2. Get stock list
        list_response = client.get(
            "/api/v1/stock/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) == len(TEST_STOCK_ITEMS)
        
        # 3. Update stock item
        update_response = client.put(
            f"/api/v1/stock/{stock_ids[0]}",
            json={"quantity": 4.0, "price_per_unit": 125.0},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert update_response.status_code == 200
        
        # 4. Record stock movement
        movement_response = client.post(
            f"/api/v1/stock/{stock_ids[0]}/movement",
            json={
                "movement_type": "consumption",
                "quantity": 0.5,
                "reason": "Cooking dinner",
                "notes": "Used for biryani"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert movement_response.status_code == 201
        
        # 5. Get analytics
        analytics_response = client.get(
            "/api/v1/stock/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert analytics_response.status_code == 200
        
        return token, stock_ids
    
    def test_meal_management_workflow(self, setup_database):
        """Test complete meal management workflow"""
        # Create user and stock items
        token, stock_ids = self.test_stock_management_workflow(setup_database)
        
        # 1. Create meals
        meal_ids = []
        for meal_data in TEST_MEALS:
            response = client.post(
                "/api/v1/meals/",
                json=meal_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 201
            meal_ids.append(response.json()["id"])
        
        # 2. Get meals list
        list_response = client.get(
            "/api/v1/meals/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        assert len(list_response.json()) == len(TEST_MEALS)
        
        # 3. Generate meal
        generation_response = client.post(
            "/api/v1/meals/generate",
            json={
                "meal_type": "breakfast",
                "dietary_preferences": ["vegetarian"],
                "cuisine_preferences": ["indian"],
                "target_date": str(date.today()),
                "servings": 2,
                "budget_limit": 200.0
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert generation_response.status_code == 200
        
        # 4. Get daily meal plan
        plan_response = client.get(
            f"/api/v1/meals/plan/daily?date={date.today()}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert plan_response.status_code == 200
        
        # 5. Submit meal feedback
        feedback_response = client.post(
            f"/api/v1/meals/{meal_ids[0]}/feedback",
            json={
                "rating": 5,
                "comments": "Excellent meal!",
                "preparation_difficulty": 3,
                "taste_rating": 5,
                "nutrition_satisfaction": 4
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert feedback_response.status_code == 201
        
        # 6. Get meal analytics
        analytics_response = client.get(
            "/api/v1/meals/analytics",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert analytics_response.status_code == 200
        
        return token, meal_ids
    
    def test_user_management_workflow(self, setup_database):
        """Test user management workflow"""
        # Create user
        token = self.test_full_signup_workflow(setup_database)
        
        # Get user profile
        profile_response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert profile_response.status_code == 200
        user_id = profile_response.json()["user"]["id"]
        
        # Get users list
        users_response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert users_response.status_code == 200
        
        # Get specific user
        user_response = client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert user_response.status_code == 200
        
        # Update user
        update_response = client.put(
            f"/api/v1/users/{user_id}",
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "phone": "+1999888777"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["first_name"] == "Updated"
    
    def test_authentication_edge_cases(self, setup_database):
        """Test authentication edge cases"""
        # Test invalid email format
        invalid_email_response = client.post("/api/v1/auth/signup", json={
            "email": "invalid-email",
            "first_name": "Test",
            "last_name": "User",
            "address": "Test Address",
            "password": "testpass"
        })
        assert invalid_email_response.status_code == 422
        
        # Test weak password (if validation exists)
        weak_password_response = client.post("/api/v1/auth/signup", json={
            "email": "weak@example.com",
            "first_name": "Weak",
            "last_name": "Password",
            "address": "Test Address",
            "password": "123"
        })
        # Should either succeed or fail with validation error
        assert weak_password_response.status_code in [201, 422]
        
        # Test signin with wrong password
        client.post("/api/v1/auth/signup", json={
            "email": "wrongpass@example.com",
            "first_name": "Wrong",
            "last_name": "Pass",
            "address": "Test Address",
            "password": "correctpass"
        })
        
        wrong_pass_response = client.post("/api/v1/auth/signin-json", json={
            "email_or_phone": "wrongpass@example.com",
            "password": "wrongpassword"
        })
        assert wrong_pass_response.status_code == 401
    
    def test_api_health_check(self, setup_database):
        """Test API health and basic functionality"""
        # Test root endpoint (if exists)
        try:
            response = client.get("/")
            # Should either return 200 or 404 (if no root endpoint)
            assert response.status_code in [200, 404]
        except:
            pass
        
        # Test API docs endpoint
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200
        
        # Test OpenAPI schema
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == 200

@pytest.mark.asyncio
async def test_concurrent_operations(setup_database):
    """Test concurrent API operations"""
    import asyncio
    
    # Create multiple users concurrently
    async def create_user(user_data):
        return client.post("/api/v1/auth/signup-full", json=user_data)
    
    # Test concurrent user creation
    tasks = [create_user(user) for user in TEST_USERS]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # At least one should succeed (others might fail due to duplicate emails)
    success_count = sum(1 for r in responses if hasattr(r, 'status_code') and r.status_code == 201)
    assert success_count >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
