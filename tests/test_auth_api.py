"""
Comprehensive API tests for authentication endpoints with dummy data
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.models.user import User, GenderEnum, DietEnum
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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

# Create test client
client = TestClient(app)

# Test data
DUMMY_USER_BASIC = {
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "address": "123 Test Street, Test City",
    "password": "testpassword123"
}

DUMMY_USER_FULL = {
    "email": "fulluser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "phone": "+1234567890",
    "country_code": "+1",
    "current_address": "456 Full Street, Full City",
    "height": 170.5,
    "weight": 65.0,
    "age": 28,
    "gender": "female",
    "diet": "vegetarian",
    "password": "fullpassword123"
}

DUMMY_SIGNIN = {
    "email_or_phone": "test@example.com",
    "password": "testpassword123"
}

DUMMY_PROFILE_COMPLETION = {
    "phone": "+1987654321",
    "country_code": "+1",
    "height": 175.0,
    "weight": 70.0,
    "age": 30,
    "gender": "male",
    "current_postal_code": "12345",
    "current_city": "Test City",
    "current_country": "Test Country",
    "native_address": "789 Native Street",
    "native_postal_code": "54321",
    "native_city": "Native City",
    "native_country": "Native Country",
    "diet": "non_vegetarian",
    "preferred_meats": ["chicken", "fish"],
    "cuisines": ["indian", "italian"],
    "is_family_account": True,
    "family_name": "Test Family",
    "is_decision_maker": True
}

@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

class TestAuthAPI:
    """Test authentication API endpoints"""
    
    def test_signup_basic(self, setup_database):
        """Test basic user signup"""
        response = client.post("/api/v1/auth/signup", json=DUMMY_USER_BASIC)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == DUMMY_USER_BASIC["email"]
        assert data["user"]["first_name"] == DUMMY_USER_BASIC["first_name"]
        assert data["user"]["profile_completed"] == False
        assert data["message"] == "User created successfully"
    
    def test_signup_duplicate_email(self, setup_database):
        """Test signup with duplicate email"""
        # First signup should succeed
        client.post("/api/v1/auth/signup", json=DUMMY_USER_BASIC)
        
        # Second signup with same email should fail
        response = client.post("/api/v1/auth/signup", json=DUMMY_USER_BASIC)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_signup_full_profile(self, setup_database):
        """Test full profile signup"""
        response = client.post("/api/v1/auth/signup-full", json=DUMMY_USER_FULL)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == DUMMY_USER_FULL["email"]
        assert data["user"]["profile_completed"] == True
        assert data["user"]["gender"] == DUMMY_USER_FULL["gender"]
        assert data["user"]["diet"] == DUMMY_USER_FULL["diet"]
    
    def test_signup_invalid_gender(self, setup_database):
        """Test signup with invalid gender"""
        invalid_data = DUMMY_USER_FULL.copy()
        invalid_data["email"] = "invalid@example.com"
        invalid_data["gender"] = "invalid_gender"
        
        response = client.post("/api/v1/auth/signup-full", json=invalid_data)
        assert response.status_code == 400
        assert "Invalid gender" in response.json()["detail"]
    
    def test_signup_invalid_diet(self, setup_database):
        """Test signup with invalid diet"""
        invalid_data = DUMMY_USER_FULL.copy()
        invalid_data["email"] = "invalid2@example.com"
        invalid_data["diet"] = "invalid_diet"
        
        response = client.post("/api/v1/auth/signup-full", json=invalid_data)
        assert response.status_code == 400
        assert "Invalid diet type" in response.json()["detail"]
    
    def test_signin_form(self, setup_database):
        """Test signin with form data"""
        # First create a user
        client.post("/api/v1/auth/signup", json=DUMMY_USER_BASIC)
        
        # Test signin
        response = client.post(
            "/api/v1/auth/signin",
            data={
                "username": DUMMY_USER_BASIC["email"],
                "password": DUMMY_USER_BASIC["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["message"] == "Login successful"
    
    def test_signin_json(self, setup_database):
        """Test signin with JSON data"""
        # First create a user
        client.post("/api/v1/auth/signup", json=DUMMY_USER_BASIC)
        
        # Test JSON signin
        response = client.post("/api/v1/auth/signin-json", json=DUMMY_SIGNIN)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["message"] == "Login successful via JSON"
    
    def test_signin_invalid_credentials(self, setup_database):
        """Test signin with invalid credentials"""
        invalid_signin = {
            "email_or_phone": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/signin-json", json=invalid_signin)
        assert response.status_code == 401
        assert "Incorrect email/phone or password" in response.json()["detail"]
    
    def test_profile_completion(self, setup_database):
        """Test profile completion"""
        # Create user and get token
        signup_response = client.post("/api/v1/auth/signup", json=DUMMY_USER_BASIC)
        token = signup_response.json()["access_token"]
        
        # Complete profile
        response = client.post(
            "/api/v1/auth/complete-profile",
            json=DUMMY_PROFILE_COMPLETION,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["profile_completed"] == True
        assert data["user"]["phone"] == DUMMY_PROFILE_COMPLETION["phone"]
        assert data["user"]["gender"] == DUMMY_PROFILE_COMPLETION["gender"]
        assert data["message"] == "Profile completed successfully"
    
    def test_profile_completion_unauthorized(self, setup_database):
        """Test profile completion without authentication"""
        response = client.post("/api/v1/auth/complete-profile", json=DUMMY_PROFILE_COMPLETION)
        assert response.status_code == 401
    
    def test_get_profile(self, setup_database):
        """Test get user profile"""
        # Create user and get token
        signup_response = client.post("/api/v1/auth/signup-full", json=DUMMY_USER_FULL)
        token = signup_response.json()["access_token"]
        
        # Get profile
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == DUMMY_USER_FULL["email"]
        assert data["user"]["profile_completed"] == True
        assert data["message"] == "Profile retrieved successfully"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
