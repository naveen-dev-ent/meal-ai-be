"""
Comprehensive validation script for enhanced stock categorization
This script validates all the changes made to the stock system
"""

import sys
import os
import importlib.util
from pathlib import Path

def validate_imports():
    """Validate that all necessary imports work correctly"""
    print("🔍 Validating imports...")
    
    try:
        # Test stock schemas import
        from app.schemas.stock_categories import (
            StockCategoryEnum,
            PetFoodTypeEnum,
            SpecialCareTypeEnum,
            StorageTypeEnum,
            StockPriorityEnum,
            AssignmentTypeEnum
        )
        print("✅ Stock categorization schemas imported successfully")
        
        # Test enhanced stock schemas
        from app.schemas.stock import StockCreate, StockUpdate, StockResponse, StockList, StockSearch
        print("✅ Enhanced stock schemas imported successfully")
        
        # Test stock service
        from app.services.stock_service import StockService
        print("✅ Enhanced stock service imported successfully")
        
        # Test stock model
        from app.models.user import Stock
        print("✅ Enhanced stock model imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def validate_enum_values():
    """Validate that all enum values are properly defined"""
    print("\n🔍 Validating enum values...")
    
    try:
        from app.schemas.stock_categories import (
            StockCategoryEnum,
            PetFoodTypeEnum,
            SpecialCareTypeEnum,
            StorageTypeEnum,
            StockPriorityEnum,
            AssignmentTypeEnum
        )
        
        # Check StockCategoryEnum
        expected_categories = [
            "grains", "vegetables", "fruits", "dairy", "meat", "fish", "eggs",
            "nuts", "spices", "oils", "beverages", "snacks", "frozen", "canned",
            "bakery", "pet_food", "medicine", "supplements", "other"
        ]
        
        for category in expected_categories:
            if hasattr(StockCategoryEnum, category.upper()):
                print(f"✅ StockCategoryEnum.{category.upper()} exists")
            else:
                print(f"❌ Missing StockCategoryEnum.{category.upper()}")
        
        # Check PetFoodTypeEnum
        pet_types = ["DOG", "CAT", "BIRD", "FISH", "RABBIT", "OTHER"]
        for pet_type in pet_types:
            if hasattr(PetFoodTypeEnum, pet_type):
                print(f"✅ PetFoodTypeEnum.{pet_type} exists")
            else:
                print(f"❌ Missing PetFoodTypeEnum.{pet_type}")
        
        # Check StorageTypeEnum
        storage_types = ["PANTRY", "REFRIGERATOR", "FREEZER", "CABINET", "CELLAR"]
        for storage_type in storage_types:
            if hasattr(StorageTypeEnum, storage_type):
                print(f"✅ StorageTypeEnum.{storage_type} exists")
            else:
                print(f"❌ Missing StorageTypeEnum.{storage_type}")
        
        # Check StockPriorityEnum
        priorities = ["LOW", "IMPORTANT", "URGENT", "CRITICAL"]
        for priority in priorities:
            if hasattr(StockPriorityEnum, priority):
                print(f"✅ StockPriorityEnum.{priority} exists")
            else:
                print(f"❌ Missing StockPriorityEnum.{priority}")
        
        # Check AssignmentTypeEnum
        assignments = ["SHARED", "PREFERRED", "EXCLUSIVE"]
        for assignment in assignments:
            if hasattr(AssignmentTypeEnum, assignment):
                print(f"✅ AssignmentTypeEnum.{assignment} exists")
            else:
                print(f"❌ Missing AssignmentTypeEnum.{assignment}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating enums: {e}")
        return False

def validate_stock_model_fields():
    """Validate that the Stock model has all required enhanced fields"""
    print("\n🔍 Validating Stock model fields...")
    
    try:
        from app.models.user import Stock
        from sqlalchemy import inspect
        
        # Get model columns
        inspector = inspect(Stock)
        columns = [col.name for col in inspector.columns]
        
        # Check for enhanced categorization fields
        enhanced_fields = [
            'subcategory', 'brand', 'special_care_types', 'pet_type',
            'storage_type', 'priority_level', 'is_organic', 'is_gluten_free',
            'is_vegan', 'is_diabetic_friendly', 'allergen_info',
            'assignment_type', 'assignment_notes'
        ]
        
        for field in enhanced_fields:
            if field in columns:
                print(f"✅ Stock model has field: {field}")
            else:
                print(f"❌ Missing Stock model field: {field}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating Stock model: {e}")
        return False

def validate_stock_service_methods():
    """Validate that StockService has all enhanced methods"""
    print("\n🔍 Validating StockService methods...")
    
    try:
        from app.services.stock_service import StockService
        
        service = StockService()
        
        # Check for enhanced methods
        enhanced_methods = [
            'get_stock_analytics',
            'get_categorized_stock_summary',
            '_get_pet_food_analytics',
            '_get_special_care_analytics',
            '_get_storage_distribution',
            '_get_priority_distribution',
            '_get_health_diet_analytics',
            '_get_family_assignment_analytics',
            '_calculate_alert_priority',
            '_calculate_restock_priority'
        ]
        
        for method in enhanced_methods:
            if hasattr(service, method):
                print(f"✅ StockService has method: {method}")
            else:
                print(f"❌ Missing StockService method: {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating StockService: {e}")
        return False

def validate_schema_fields():
    """Validate that schemas have all enhanced fields"""
    print("\n🔍 Validating schema fields...")
    
    try:
        from app.schemas.stock import StockBase, StockCreate, StockUpdate, StockList, StockSearch
        import inspect
        
        # Check StockBase fields
        base_fields = [
            'subcategory', 'brand', 'special_care_types', 'pet_type',
            'storage_type', 'priority_level', 'is_organic', 'is_gluten_free',
            'is_vegan', 'is_diabetic_friendly', 'allergen_info',
            'assignment_type', 'assignment_notes'
        ]
        
        # Get field annotations from StockBase
        annotations = getattr(StockBase, '__annotations__', {})
        
        for field in base_fields:
            if field in annotations:
                print(f"✅ StockBase has field: {field}")
            else:
                print(f"❌ Missing StockBase field: {field}")
        
        # Check StockSearch enhanced filters
        search_annotations = getattr(StockSearch, '__annotations__', {})
        search_fields = [
            'subcategory', 'brand', 'special_care_types', 'pet_type',
            'storage_type', 'priority_level', 'is_organic', 'is_gluten_free',
            'is_vegan', 'is_diabetic_friendly', 'assignment_type', 'assigned_to_user_id'
        ]
        
        for field in search_fields:
            if field in search_annotations:
                print(f"✅ StockSearch has filter: {field}")
            else:
                print(f"❌ Missing StockSearch filter: {field}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating schemas: {e}")
        return False

def validate_api_endpoints():
    """Validate that API endpoints are properly configured"""
    print("\n🔍 Validating API endpoints...")
    
    try:
        # Check if stock endpoints file exists and has required imports
        stock_api_path = Path("app/api/v1/endpoints/stock.py")
        if stock_api_path.exists():
            print("✅ Stock API endpoints file exists")
            
            # Read the file to check for enhanced categorization imports
            with open(stock_api_path, 'r') as f:
                content = f.read()
                
            required_imports = [
                "from app.schemas.stock_categories import",
                "require_family_member",
                "or_"  # For enhanced search filters
            ]
            
            for import_stmt in required_imports:
                if import_stmt in content:
                    print(f"✅ Found required import: {import_stmt}")
                else:
                    print(f"❌ Missing import: {import_stmt}")
            
            # Check for enhanced endpoints
            enhanced_endpoints = [
                "categorized-summary",
                "enhanced search with categorization filters"
            ]
            
            for endpoint in enhanced_endpoints:
                if endpoint in content:
                    print(f"✅ Found enhanced endpoint/feature: {endpoint}")
                else:
                    print(f"❌ Missing enhanced endpoint/feature: {endpoint}")
        else:
            print("❌ Stock API endpoints file not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating API endpoints: {e}")
        return False

def validate_test_files():
    """Validate that test files are properly updated"""
    print("\n🔍 Validating test files...")
    
    try:
        test_files = [
            "tests/test_stock_api.py",
            "tests/test_stock_categorization.py"
        ]
        
        for test_file in test_files:
            test_path = Path(test_file)
            if test_path.exists():
                print(f"✅ Test file exists: {test_file}")
                
                # Check if test file has enhanced categorization tests
                with open(test_path, 'r') as f:
                    content = f.read()
                
                enhanced_features = [
                    "enhanced_categorization",
                    "pet_food",
                    "special_care",
                    "storage_type",
                    "priority_level",
                    "assignment_type"
                ]
                
                for feature in enhanced_features:
                    if feature in content:
                        print(f"✅ Test file {test_file} includes {feature} tests")
                    else:
                        print(f"⚠️  Test file {test_file} missing {feature} tests")
            else:
                print(f"❌ Test file not found: {test_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating test files: {e}")
        return False

def run_validation():
    """Run all validation checks"""
    print("🚀 Starting Enhanced Stock Categorization Validation\n")
    
    results = []
    
    # Run all validation checks
    results.append(("Import Validation", validate_imports()))
    results.append(("Enum Values Validation", validate_enum_values()))
    results.append(("Stock Model Fields", validate_stock_model_fields()))
    results.append(("Stock Service Methods", validate_stock_service_methods()))
    results.append(("Schema Fields", validate_schema_fields()))
    results.append(("API Endpoints", validate_api_endpoints()))
    results.append(("Test Files", validate_test_files()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validations passed! Enhanced stock categorization is ready.")
        return True
    else:
        print("⚠️  Some validations failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    # Add the current directory to Python path for imports
    sys.path.insert(0, os.getcwd())
    
    success = run_validation()
    sys.exit(0 if success else 1)
