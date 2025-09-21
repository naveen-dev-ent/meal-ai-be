"""
API tests for stock endpoints with dummy data
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, datetime

from app.core.database import Base, get_db
from main import app
import io
import csv

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_stock.db"
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
    "email": "stocktest@example.com",
    "first_name": "Stock",
    "last_name": "Tester",
    "phone": "+1234567890",
    "country_code": "+1",
    "current_address": "123 Stock Street",
    "height": 170.0,
    "weight": 65.0,
    "age": 30,
    "gender": "male",
    "diet": "non_vegetarian",
    "password": "stocktest123"
}

DUMMY_STOCK_CREATE = {
    "item_name": "Basmati Rice",
    "category": "grains",
    "subcategory": "long_grain",
    "brand": "India Gate",
    "weight": 5.0,
    "unit": "kg",
    "current_quantity": 5.0,
    "minimum_quantity": 1.0,
    "price_per_unit": 120.0,
    "expiry_date": str(date(2024, 12, 31)),
    "is_perishable": False,
    "requires_refrigeration": False,
    "is_special_care_item": False,
    "is_pet_food": False,
    "storage_type": "pantry",
    "priority_level": "important",
    "is_organic": True,
    "is_gluten_free": True,
    "is_vegan": True,
    "is_diabetic_friendly": False,
    "assignment_type": "shared"
}

DUMMY_STOCK_UPDATE = {
    "current_quantity": 3.0,
    "price_per_unit": 125.0,
    "minimum_quantity": 0.5,
    "brand": "Fortune",
    "is_organic": False,
    "priority_level": "urgent"
}

DUMMY_STOCK_MOVEMENT = {
    "stock_id": 1,
    "quantity_change": -0.5,
    "movement_type": "consumption",
    "reason": "Used for dinner preparation",
    "notes": "Made biryani for family"
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

class TestStockAPI:
    """Test stock management API endpoints"""
    
    def test_create_stock_item(self, auth_token):
        """Test create stock item"""
        response = client.post(
            "/api/v1/stock/",
            json=DUMMY_STOCK_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["item_name"] == DUMMY_STOCK_CREATE["item_name"]
        assert data["category"] == DUMMY_STOCK_CREATE["category"]
        assert data["current_quantity"] == DUMMY_STOCK_CREATE["current_quantity"]
        assert data["brand"] == DUMMY_STOCK_CREATE["brand"]
        assert data["is_organic"] == DUMMY_STOCK_CREATE["is_organic"]
    
    def test_get_stock_list(self, auth_token):
        """Test get stock list"""
        # Create a stock item first
        client.post(
            "/api/v1/stock/",
            json=DUMMY_STOCK_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        response = client.get(
            "/api/v1/stock/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_stock_with_filters(self, auth_token):
        """Test get stock with category filter"""
        response = client.get(
            "/api/v1/stock/?category=grains",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_stock_item(self, auth_token):
        """Test update stock item"""
        # Create stock item first
        create_response = client.post(
            "/api/v1/stock/",
            json=DUMMY_STOCK_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        stock_id = create_response.json()["id"]
        
        # Update stock item
        response = client.put(
            f"/api/v1/stock/{stock_id}",
            json=DUMMY_STOCK_UPDATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_quantity"] == DUMMY_STOCK_UPDATE["current_quantity"]
        assert data["brand"] == DUMMY_STOCK_UPDATE["brand"]
        assert data["priority_level"] == DUMMY_STOCK_UPDATE["priority_level"]
        assert data["price_per_unit"] == DUMMY_STOCK_UPDATE["price_per_unit"]
    
    def test_record_stock_movement(self, auth_token):
        """Test record stock movement"""
        # Create stock item first
        create_response = client.post(
            "/api/v1/stock/",
            json=DUMMY_STOCK_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        stock_id = create_response.json()["id"]
        
        # Record movement
        response = client.post(
            f"/api/v1/stock/{stock_id}/movement",
            json=DUMMY_STOCK_MOVEMENT,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["movement_type"] == DUMMY_STOCK_MOVEMENT["movement_type"]
        assert data["quantity_change"] == DUMMY_STOCK_MOVEMENT["quantity_change"]
    
    def test_get_stock_analytics(self, auth_token):
        """Test get stock analytics"""
        response = client.get(
            "/api/v1/stock/analytics",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_items" in data
        assert "total_value" in data
        assert "low_stock_items" in data
        assert "pet_food_analytics" in data
        assert "special_care_analytics" in data
        assert "storage_distribution" in data
        assert "priority_distribution" in data
        assert "health_diet_analytics" in data
        assert "family_assignment_analytics" in data
    
    def test_get_low_stock_alerts(self, auth_token):
        """Test get low stock alerts"""
        response = client.get(
            "/api/v1/stock/alerts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_search_stock(self, auth_token):
        """Test stock search"""
        # Create stock item first
        client.post(
            "/api/v1/stock/",
            json=DUMMY_STOCK_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        response = client.get(
            "/api/v1/stock/?query=rice",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_delete_stock_item(self, auth_token):
        """Test delete stock item"""
        # Create stock item first
        create_response = client.post(
            "/api/v1/stock/",
            json=DUMMY_STOCK_CREATE,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        stock_id = create_response.json()["id"]
        
        # Delete stock item
        response = client.delete(
            f"/api/v1/stock/{stock_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204
    
    def test_enhanced_categorization_filters(self, auth_token):
        """Test enhanced categorization filters"""
        # Create pet food item
        pet_food_data = {
            **DUMMY_STOCK_CREATE,
            "item_name": "Dog Food Premium",
            "category": "pet_food",
            "is_pet_food": True,
            "pet_type": "dog",
            "priority_level": "urgent"
        }
        
        client.post(
            "/api/v1/stock/",
            json=pet_food_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Test pet food filter
        response = client.get(
            "/api/v1/stock/?is_pet_food=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(item["is_pet_food"] for item in data)
    
    def test_special_care_items(self, auth_token):
        """Test special care items functionality"""
        special_care_data = {
            **DUMMY_STOCK_CREATE,
            "item_name": "Diabetic Sugar Free Cookies",
            "category": "snacks",
            "is_special_care_item": True,
            "is_diabetic_friendly": True,
            "special_care_types": ["diabetic", "low_sugar"],
            "priority_level": "critical"
        }
        
        response = client.post(
            "/api/v1/stock/",
            json=special_care_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_special_care_item"] == True
        assert data["is_diabetic_friendly"] == True
        assert data["priority_level"] == "critical"
    
    def test_health_diet_filters(self, auth_token):
        """Test health and diet filters"""
        # Test organic filter
        response = client.get(
            "/api/v1/stock/?is_organic=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Test vegan filter
        response = client.get(
            "/api/v1/stock/?is_vegan=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_storage_and_priority_filters(self, auth_token):
        """Test storage type and priority level filters"""
        # Test storage type filter
        response = client.get(
            "/api/v1/stock/?storage_type=pantry",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Test priority level filter
        response = client.get(
            "/api/v1/stock/?priority_level=important",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_categorized_summary_endpoint(self, auth_token):
        """Test categorized stock summary endpoint"""
        response = client.get(
            "/api/v1/stock/categorized-summary",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_items" in data
        assert "categories" in data
        assert "special_categories" in data
        assert "storage_summary" in data
        assert "priority_summary" in data
        
        # Check special categories structure
        special_cats = data["special_categories"]
        assert "pet_food" in special_cats
        assert "special_care" in special_cats
        assert "organic" in special_cats
        assert "dietary_restrictions" in special_cats
    
    def test_brand_and_subcategory_search(self, auth_token):
        """Test brand and subcategory search functionality"""
        # Test brand search
        response = client.get(
            "/api/v1/stock/?brand=India",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Test subcategory search
        response = client.get(
            "/api/v1/stock/?subcategory=long_grain",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_assignment_type_functionality(self, auth_token):
        """Test family assignment type functionality"""
        exclusive_item_data = {
            **DUMMY_STOCK_CREATE,
            "item_name": "Special Medicine",
            "category": "medicine",
            "assignment_type": "exclusive",
            "assignment_notes": "Only for John due to allergy",
            "is_special_care_item": True
        }
        
        response = client.post(
            "/api/v1/stock/",
            json=exclusive_item_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["assignment_type"] == "exclusive"
        assert data["assignment_notes"] == "Only for John due to allergy"
    
    def test_unauthorized_stock_access(self, setup_database):
        """Test unauthorized access to stock endpoints"""
        response = client.get("/api/v1/stock/")
        assert response.status_code == 401

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
