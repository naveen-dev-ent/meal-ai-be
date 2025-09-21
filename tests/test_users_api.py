"""
API tests for user endpoints with dummy data
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_users.db"
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
    "email": "usertest@example.com",
    "first_name": "User",
    "last_name": "Test",
    "address": "123 User Street",
    "password": "usertest123"
}

DUMMY_USER_UPDATE = {
    "first_name": "Updated",
    "last_name": "User",
    "phone": "+1111111111",
    "height": 180.0,
    "weight": 75.0
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
    response = client.post("/api/v1/auth/signup", json=DUMMY_USER)
    return response.json()["access_token"]

class TestUsersAPI:
    """Test user management API endpoints"""
    
    def test_get_users_list(self, auth_token):
        """Test get users list"""
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_user_by_id(self, auth_token):
        """Test get specific user by ID"""
        # Get current user ID from profile
        profile_response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_id = profile_response.json()["user"]["id"]
        
        response = client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == DUMMY_USER["email"]
    
    def test_update_user(self, auth_token):
        """Test update user information"""
        # Get current user ID
        profile_response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_id = profile_response.json()["user"]["id"]
        
        response = client.put(
            f"/api/v1/users/{user_id}",
            json=DUMMY_USER_UPDATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == DUMMY_USER_UPDATE["first_name"]
        assert data["phone"] == DUMMY_USER_UPDATE["phone"]
    
    def test_get_nonexistent_user(self, auth_token):
        """Test get non-existent user"""
        response = client.get(
            "/api/v1/users/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_unauthorized_access(self, setup_database):
        """Test unauthorized access to user endpoints"""
        response = client.get("/api/v1/users/")
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
