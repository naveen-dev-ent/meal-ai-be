"""Debug schema validation issues"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    try:
        from pydantic import BaseModel, EmailStr, validator, Field
        from typing import Optional, List, Dict, Any
        from enum import Enum
        print("✅ Basic imports OK")
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_enum_definitions():
    try:
        from app.schemas.auth import GenderEnum, DietEnum, DiningStyleEnum
        print("✅ Enum definitions OK")
        
        # Test enum values
        print(f"Gender options: {list(GenderEnum)}")
        print(f"Diet options: {list(DietEnum)}")
        return True
    except Exception as e:
        print(f"❌ Enum definitions failed: {e}")
        return False

def test_basic_schema():
    try:
        from app.schemas.auth import UserSignUpBasic
        
        # Test valid data
        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street, Test City"
        }
        
        user = UserSignUpBasic(**data)
        print("✅ UserSignUpBasic validation OK")
        return True
    except Exception as e:
        print(f"❌ UserSignUpBasic validation failed: {e}")
        return False

def test_full_schema():
    try:
        from app.schemas.auth import UserSignUp, GenderEnum, DietEnum
        
        # Test valid data
        data = {
            "email": "full@example.com",
            "phone": "+1234567890",
            "password": "fullpass123",
            "country_code": "+1",
            "first_name": "Full",
            "last_name": "User",
            "height": 170.0,
            "weight": 65.0,
            "age": 25,
            "gender": GenderEnum.FEMALE,
            "current_address": "456 Full Street",
            "current_postal_code": "12345",
            "current_city": "Test City",
            "current_country": "USA",
            "native_address": "789 Native Street",
            "native_postal_code": "54321",
            "native_city": "Native City",
            "native_country": "Native Country",
            "diet": DietEnum.VEGETARIAN,
            "cuisines": ["indian", "italian"]
        }
        
        user = UserSignUp(**data)
        print("✅ UserSignUp validation OK")
        return True
    except Exception as e:
        print(f"❌ UserSignUp validation failed: {e}")
        return False

def main():
    print("🔍 DEBUGGING SCHEMA VALIDATION")
    print("=" * 40)
    
    all_passed = True
    
    if not test_basic_imports():
        all_passed = False
    
    if not test_enum_definitions():
        all_passed = False
    
    if not test_basic_schema():
        all_passed = False
    
    if not test_full_schema():
        all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ ALL SCHEMA TESTS PASSED!")
    else:
        print("❌ SCHEMA VALIDATION FAILED!")
    print("=" * 40)

if __name__ == "__main__":
    main()
