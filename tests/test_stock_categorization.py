"""
Test cases for enhanced stock categorization features
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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_stock_categorization.db"
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
    "email": "categorization@example.com",
    "first_name": "Category",
    "last_name": "Tester",
    "phone": "+1234567890",
    "country_code": "+1",
    "current_address": "123 Category Street",
    "height": 170.0,
    "weight": 65.0,
    "age": 30,
    "gender": "male",
    "diet": "non_vegetarian",
    "password": "categorytest123"
}

# Enhanced stock items for testing
STOCK_ITEMS = [
    {
        "item_name": "Organic Brown Rice",
        "category": "grains",
        "subcategory": "whole_grain",
        "brand": "Organic Valley",
        "weight": 2.0,
        "unit": "kg",
        "current_quantity": 2.0,
        "minimum_quantity": 0.5,
        "price_per_unit": 180.0,
        "is_organic": True,
        "is_gluten_free": True,
        "is_vegan": True,
        "storage_type": "pantry",
        "priority_level": "important",
        "assignment_type": "shared"
    },
    {
        "item_name": "Premium Dog Food",
        "category": "pet_food",
        "subcategory": "dry_food",
        "brand": "Royal Canin",
        "weight": 5.0,
        "unit": "kg",
        "current_quantity": 5.0,
        "minimum_quantity": 1.0,
        "price_per_unit": 2500.0,
        "is_pet_food": True,
        "pet_type": "dog",
        "storage_type": "pantry",
        "priority_level": "urgent",
        "assignment_type": "shared"
    },
    {
        "item_name": "Diabetic Cookies",
        "category": "snacks",
        "subcategory": "sugar_free",
        "brand": "Diabetic Delight",
        "weight": 0.5,
        "unit": "kg",
        "current_quantity": 0.5,
        "minimum_quantity": 0.1,
        "price_per_unit": 350.0,
        "is_special_care_item": True,
        "special_care_types": ["diabetic", "low_sugar"],
        "is_diabetic_friendly": True,
        "storage_type": "pantry",
        "priority_level": "critical",
        "assignment_type": "exclusive",
        "assignment_notes": "Only for diabetic family member"
    },
    {
        "item_name": "Gluten-Free Bread",
        "category": "bakery",
        "subcategory": "gluten_free",
        "brand": "Free From",
        "weight": 0.4,
        "unit": "kg",
        "current_quantity": 0.4,
        "minimum_quantity": 0.2,
        "price_per_unit": 250.0,
        "is_gluten_free": True,
        "requires_refrigeration": True,
        "storage_type": "refrigerator",
        "priority_level": "important",
        "assignment_type": "preferred"
    },
    {
        "item_name": "Frozen Vegetables",
        "category": "vegetables",
        "subcategory": "frozen",
        "brand": "Green Valley",
        "weight": 1.0,
        "unit": "kg",
        "current_quantity": 1.0,
        "minimum_quantity": 0.5,
        "price_per_unit": 120.0,
        "is_vegan": True,
        "requires_refrigeration": True,
        "storage_type": "freezer",
        "priority_level": "important",
        "assignment_type": "shared"
    }
]

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

@pytest.fixture
def populated_stock(auth_token):
    """Create multiple stock items for testing"""
    stock_ids = []
    for item in STOCK_ITEMS:
        response = client.post(
            "/api/v1/stock/",
            json=item,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 201:
            stock_ids.append(response.json()["id"])
    return stock_ids

class TestStockCategorization:
    """Test enhanced stock categorization features"""
    
    def test_category_enum_validation(self, auth_token):
        """Test that category enum validation works"""
        invalid_category_item = {
            **STOCK_ITEMS[0],
            "category": "invalid_category"
        }
        
        response = client.post(
            "/api/v1/stock/",
            json=invalid_category_item,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_pet_food_categorization(self, auth_token, populated_stock):
        """Test pet food specific categorization"""
        # Filter by pet food
        response = client.get(
            "/api/v1/stock/?is_pet_food=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        pet_food_item = next((item for item in data if item["is_pet_food"]), None)
        assert pet_food_item is not None
        assert pet_food_item["pet_type"] == "dog"
        assert pet_food_item["priority_level"] == "urgent"
    
    def test_special_care_categorization(self, auth_token, populated_stock):
        """Test special care items categorization"""
        # Filter by special care
        response = client.get(
            "/api/v1/stock/?is_special_care=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        special_care_item = next((item for item in data if item["is_special_care_item"]), None)
        assert special_care_item is not None
        assert special_care_item["is_diabetic_friendly"] == True
        assert special_care_item["priority_level"] == "critical"
        assert special_care_item["assignment_type"] == "exclusive"
    
    def test_health_diet_filters(self, auth_token, populated_stock):
        """Test health and diet specific filters"""
        # Test organic filter
        response = client.get(
            "/api/v1/stock/?is_organic=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        organic_data = response.json()
        assert len(organic_data) >= 1
        assert all(item["is_organic"] for item in organic_data)
        
        # Test gluten-free filter
        response = client.get(
            "/api/v1/stock/?is_gluten_free=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        gf_data = response.json()
        assert len(gf_data) >= 1
        assert all(item["is_gluten_free"] for item in gf_data)
        
        # Test vegan filter
        response = client.get(
            "/api/v1/stock/?is_vegan=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        vegan_data = response.json()
        assert len(vegan_data) >= 1
        assert all(item["is_vegan"] for item in vegan_data)
    
    def test_storage_type_filters(self, auth_token, populated_stock):
        """Test storage type filtering"""
        # Test pantry storage
        response = client.get(
            "/api/v1/stock/?storage_type=pantry",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        pantry_data = response.json()
        assert len(pantry_data) >= 1
        assert all(item["storage_type"] == "pantry" for item in pantry_data)
        
        # Test refrigerator storage
        response = client.get(
            "/api/v1/stock/?storage_type=refrigerator",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        fridge_data = response.json()
        assert len(fridge_data) >= 1
        assert all(item["storage_type"] == "refrigerator" for item in fridge_data)
        
        # Test freezer storage
        response = client.get(
            "/api/v1/stock/?storage_type=freezer",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        freezer_data = response.json()
        assert len(freezer_data) >= 1
        assert all(item["storage_type"] == "freezer" for item in freezer_data)
    
    def test_priority_level_filters(self, auth_token, populated_stock):
        """Test priority level filtering"""
        # Test critical priority
        response = client.get(
            "/api/v1/stock/?priority_level=critical",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        critical_data = response.json()
        assert len(critical_data) >= 1
        assert all(item["priority_level"] == "critical" for item in critical_data)
        
        # Test urgent priority
        response = client.get(
            "/api/v1/stock/?priority_level=urgent",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        urgent_data = response.json()
        assert len(urgent_data) >= 1
        assert all(item["priority_level"] == "urgent" for item in urgent_data)
    
    def test_assignment_type_filters(self, auth_token, populated_stock):
        """Test assignment type filtering"""
        # Test exclusive assignment
        response = client.get(
            "/api/v1/stock/?assignment_type=exclusive",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        exclusive_data = response.json()
        assert len(exclusive_data) >= 1
        assert all(item["assignment_type"] == "exclusive" for item in exclusive_data)
        
        # Test shared assignment
        response = client.get(
            "/api/v1/stock/?assignment_type=shared",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        shared_data = response.json()
        assert len(shared_data) >= 1
        assert all(item["assignment_type"] == "shared" for item in shared_data)
    
    def test_brand_and_subcategory_search(self, auth_token, populated_stock):
        """Test brand and subcategory search"""
        # Test brand search
        response = client.get(
            "/api/v1/stock/?brand=Organic",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        brand_data = response.json()
        assert len(brand_data) >= 1
        
        # Test subcategory search
        response = client.get(
            "/api/v1/stock/?subcategory=whole_grain",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        subcat_data = response.json()
        assert len(subcat_data) >= 1
    
    def test_enhanced_analytics(self, auth_token, populated_stock):
        """Test enhanced analytics with categorization"""
        response = client.get(
            "/api/v1/stock/analytics",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        analytics = response.json()
        
        # Check basic analytics
        assert "total_items" in analytics
        assert "total_value" in analytics
        assert analytics["total_items"] >= len(STOCK_ITEMS)
        
        # Check enhanced categorization analytics
        assert "pet_food_analytics" in analytics
        assert "special_care_analytics" in analytics
        assert "storage_distribution" in analytics
        assert "priority_distribution" in analytics
        assert "health_diet_analytics" in analytics
        assert "family_assignment_analytics" in analytics
        
        # Verify pet food analytics structure
        pet_analytics = analytics["pet_food_analytics"]
        assert "total_items" in pet_analytics
        assert "total_value" in pet_analytics
        assert "pet_types" in pet_analytics
        
        # Verify special care analytics structure
        special_analytics = analytics["special_care_analytics"]
        assert "total_items" in special_analytics
        assert "total_value" in special_analytics
        assert "care_types" in special_analytics
        assert "assigned_users" in special_analytics
        
        # Verify health diet analytics
        health_analytics = analytics["health_diet_analytics"]
        assert "organic_items" in health_analytics
        assert "gluten_free_items" in health_analytics
        assert "vegan_items" in health_analytics
        assert "diabetic_friendly_items" in health_analytics
    
    def test_categorized_summary(self, auth_token, populated_stock):
        """Test categorized stock summary endpoint"""
        response = client.get(
            "/api/v1/stock/categorized-summary",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        summary = response.json()
        
        # Check main structure
        assert "total_items" in summary
        assert "categories" in summary
        assert "special_categories" in summary
        assert "storage_summary" in summary
        assert "priority_summary" in summary
        
        # Check categories breakdown
        categories = summary["categories"]
        assert isinstance(categories, dict)
        
        # Check special categories
        special_cats = summary["special_categories"]
        assert "pet_food" in special_cats
        assert "special_care" in special_cats
        assert "organic" in special_cats
        assert "dietary_restrictions" in special_cats
        
        # Verify dietary restrictions structure
        dietary = special_cats["dietary_restrictions"]
        assert "gluten_free" in dietary
        assert "vegan" in dietary
        assert "diabetic_friendly" in dietary
        
        # Check storage and priority summaries
        storage_summary = summary["storage_summary"]
        assert "pantry" in storage_summary
        
        priority_summary = summary["priority_summary"]
        assert isinstance(priority_summary, dict)
    
    def test_combined_filters(self, auth_token, populated_stock):
        """Test multiple filters combined"""
        # Test organic + vegan combination
        response = client.get(
            "/api/v1/stock/?is_organic=true&is_vegan=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all(item["is_organic"] and item["is_vegan"] for item in data)
        
        # Test storage + priority combination
        response = client.get(
            "/api/v1/stock/?storage_type=pantry&priority_level=critical",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
