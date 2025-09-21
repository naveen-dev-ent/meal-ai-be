"""
API tests for meal endpoints with dummy data
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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_meals.db"
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

# Test data
DUMMY_USER = {
    "email": "mealtest@example.com",
    "first_name": "Meal",
    "last_name": "Tester",
    "phone": "+1234567890",
    "country_code": "+1",
    "current_address": "123 Meal Street",
    "height": 170.0,
    "weight": 65.0,
    "age": 25,
    "gender": "female",
    "diet": "vegetarian",
    "password": "mealtest123"
}

DUMMY_MEAL_CREATE = {
    "name": "Test Breakfast",
    "meal_type": "breakfast",
    "ingredients": ["oats", "milk", "banana"],
    "instructions": "Mix oats with milk, add banana slices",
    "prep_time": 10,
    "cook_time": 5,
    "servings": 2,
    "calories_per_serving": 250,
    "scheduled_for": str(date.today())
}

DUMMY_MEAL_GENERATION = {
    "meal_type": "lunch",
    "dietary_preferences": ["vegetarian"],
    "cuisine_preferences": ["indian"],
    "target_date": str(date.today()),
    "servings": 4,
    "budget_limit": 500.0
}

DUMMY_MEAL_FEEDBACK = {
    "rating": 4,
    "comments": "Delicious meal, loved it!",
    "preparation_difficulty": 3,
    "taste_rating": 5,
    "nutrition_satisfaction": 4
}

@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_token(setup_database):
    """Create user and return auth token"""
    response = client.post("/api/v1/auth/signup-full", json=DUMMY_USER)
    return response.json()["access_token"]

class TestMealsAPI:
    """Test meal management API endpoints"""
    
    def test_create_meal(self, auth_token):
        """Test create meal"""
        response = client.post(
            "/api/v1/meals/",
            json=DUMMY_MEAL_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == DUMMY_MEAL_CREATE["name"]
        assert data["meal_type"] == DUMMY_MEAL_CREATE["meal_type"]
        assert data["servings"] == DUMMY_MEAL_CREATE["servings"]
    
    def test_get_meals_list(self, auth_token):
        """Test get meals list"""
        # Create a meal first
        client.post(
            "/api/v1/meals/",
            json=DUMMY_MEAL_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        response = client.get(
            "/api/v1/meals/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_meals_with_filters(self, auth_token):
        """Test get meals with date and type filters"""
        response = client.get(
            f"/api/v1/meals/?start_date={date.today()}&meal_type=breakfast",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_generate_meal(self, auth_token):
        """Test meal generation"""
        response = client.post(
            "/api/v1/meals/generate",
            json=DUMMY_MEAL_GENERATION,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "meal" in data
        assert "ingredients" in data
        assert data["meal"]["meal_type"] == DUMMY_MEAL_GENERATION["meal_type"]
    
    def test_get_daily_meal_plan(self, auth_token):
        """Test get daily meal plan"""
        response = client.get(
            f"/api/v1/meals/plan/daily?date={date.today()}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "date" in data
        assert "meals" in data
    
    def test_meal_feedback(self, auth_token):
        """Test meal feedback submission"""
        # Create a meal first
        meal_response = client.post(
            "/api/v1/meals/",
            json=DUMMY_MEAL_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        meal_id = meal_response.json()["id"]
        
        # Submit feedback
        response = client.post(
            f"/api/v1/meals/{meal_id}/feedback",
            json=DUMMY_MEAL_FEEDBACK,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == DUMMY_MEAL_FEEDBACK["rating"]
        assert data["comments"] == DUMMY_MEAL_FEEDBACK["comments"]
    
    def test_get_meal_history(self, auth_token):
        """Test get meal history"""
        response = client.get(
            "/api/v1/meals/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_meal_analytics(self, auth_token):
        """Test get meal analytics"""
        response = client.get(
            "/api/v1/meals/analytics",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_meals" in data
        assert "avg_rating" in data
    
    def test_unauthorized_meal_access(self, setup_database):
        """Test unauthorized access to meal endpoints"""
        response = client.get("/api/v1/meals/")
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
