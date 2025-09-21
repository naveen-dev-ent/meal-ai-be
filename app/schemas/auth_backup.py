from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    TRANSGENDER = "transgender"
    OTHER = "other"


class DietEnum(str, Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    EGGETARIAN = "eggetarian"
    NON_VEGETARIAN = "non_vegetarian"


class DiningStyleEnum(str, Enum):
    FIVE_STAR = "5_star"
    STREET_SIDE = "street_side"
    OTHER = "other"


class UserSignUpBasic(BaseModel):
    """Basic user signup schema - minimal required fields"""
    
    # Authentication
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    # Basic Personal Information
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    
    # Basic Address
    address: str = Field(..., min_length=10)


class UserSignUp(BaseModel):
    """User signup schema with comprehensive profile data"""
    
    # Authentication
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8)
    country_code: str = Field(..., min_length=1, max_length=5)
    
    # Personal Information
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    height: float = Field(..., gt=0, le=300)  # in cm
    weight: float = Field(..., gt=0, le=500)  # in kg
    age: int = Field(..., gt=0, le=120)
    gender: GenderEnum
    
    # Addresses
    current_address: str = Field(..., min_length=10)
    current_postal_code: str = Field(..., min_length=3, max_length=20)
    current_city: str = Field(..., min_length=2, max_length=100)
    current_country: str = Field(..., min_length=2, max_length=100)
    
    native_address: str = Field(..., min_length=10)
    native_postal_code: str = Field(..., min_length=3, max_length=20)
    native_city: str = Field(..., min_length=2, max_length=100)
    native_country: str = Field(..., min_length=2, max_length=100)
    
    # Budget
    daily_budget: Optional[float] = Field(None, gt=0)
    monthly_budget: Optional[float] = Field(None, gt=0)
    one_time_budget: Optional[float] = Field(None, gt=0)
    
    # Health and Diet
    diet: DietEnum
    preferred_meats: Optional[List[str]] = None  # for non-vegetarians
    health_conditions: Optional[List[str]] = None
    vitamin_deficiencies: Optional[List[str]] = None
    
    # Preferences
    meal_styles: Optional[List[str]] = None  # junk, healthy, spicy, tasty
    cuisines: List[str] = Field(..., min_items=2, max_items=6)  # mandatory + optional
    dining_style: Optional[DiningStyleEnum] = None
    
    # Family Settings
    is_family_account: bool = False
    family_name: Optional[str] = None
    meal_frequency: Optional[int] = Field(None, ge=1, le=6)  # meals per day
    meal_timings: Optional[List[str]] = None  # meal times
    
    # Chef Settings
    is_chef: bool = False
    chef_availability: Optional[Dict[str, Any]] = None
    
    # Special Needs
    has_special_needs: bool = False
    special_needs_details: Optional[Dict[str, Any]] = None
    
    # Pets
    has_pets: bool = False
    pets_info: Optional[Dict[str, Any]] = None
    
    # Religion and Festivals
    religion: Optional[str] = None
    festival_preferences: Optional[Dict[str, Any]] = None
    
    # Refrigeration
    has_refrigeration: Optional[bool] = None
    
    # Meal Generation Preferences
    meal_generation_criteria: List[str] = Field(default=["stock", "region", "native"])
    meal_timing_preference: str = Field(default="18:00", pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    
    # Office Meals
    needs_office_meals: bool = False
    office_meal_preferences: Optional[Dict[str, Any]] = None
    
    @field_validator('cuisines')
    @classmethod
    def validate_cuisines(cls, v):
        """Validate cuisine selection"""
        if len(v) < 2:
            raise ValueError("At least 2 cuisines are required")
        if len(v) > 6:
            raise ValueError("Maximum 6 cuisines allowed")
        return v


class UserSignIn(BaseModel):
    """User signin schema"""
    username: str = Field(..., description="Email or phone number")
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str
    user_id: int
    message: str


class UserProfileResponse(BaseModel):
    """User profile response schema"""
    user: Dict[str, Any]  # User model data
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    message: str
    
    class Config:
        from_attributes = True


class FamilyCreate(BaseModel):
    """Family member creation schema"""
    
    # Authentication
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8)
    
    # Personal Information
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    height: float = Field(..., gt=0, le=300)
    weight: float = Field(..., gt=0, le=500)
    age: int = Field(..., gt=0, le=120)
    gender: GenderEnum
    
    # Health and Diet
    diet: DietEnum
    preferred_meats: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    vitamin_deficiencies: Optional[List[str]] = None
    
    # Preferences
    meal_styles: Optional[List[str]] = None
    cuisines: List[str] = Field(..., min_items=2, max_items=6)
    dining_style: Optional[DiningStyleEnum] = None
    
    # Special Settings
    is_chef: bool = False
    chef_availability: Optional[Dict[str, Any]] = None
    has_special_needs: bool = False
    special_needs_details: Optional[Dict[str, Any]] = None
    needs_office_meals: bool = False
    office_meal_preferences: Optional[Dict[str, Any]] = None
    
    # Religion
    religion: Optional[str] = None
    
    @validator('preferred_meats')
    def validate_meats_for_diet(cls, v, values):
        """Validate meat preferences for non-vegetarian diet"""
        if values.get('diet') == DietEnum.NON_VEGETARIAN and not v:
            raise ValueError("Meat preferences are required for non-vegetarian diet")
        return v


class UserUpdate(BaseModel):
    """User profile update schema"""
    
    # Personal Information
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    height: Optional[float] = Field(None, gt=0, le=300)
    weight: Optional[float] = Field(None, gt=0, le=500)
    
    # Addresses
    current_address: Optional[str] = Field(None, min_length=10)
    current_postal_code: Optional[str] = Field(None, min_length=3, max_length=20)
    current_city: Optional[str] = Field(None, min_length=2, max_length=100)
    current_country: Optional[str] = Field(None, min_length=2, max_length=100)
    
    native_address: Optional[str] = Field(None, min_length=10)
    native_postal_code: Optional[str] = Field(None, min_length=3, max_length=20)
    native_city: Optional[str] = Field(None, min_length=2, max_length=100)
    native_country: Optional[str] = Field(None, min_length=2, max_length=100)
    
    # Budget
    daily_budget: Optional[float] = Field(None, gt=0)
    monthly_budget: Optional[float] = Field(None, gt=0)
    one_time_budget: Optional[float] = Field(None, gt=0)
    
    # Health and Diet
    diet: Optional[DietEnum] = None
    preferred_meats: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    vitamin_deficiencies: Optional[List[str]] = None
    
    # Preferences
    meal_styles: Optional[List[str]] = None
    cuisines: Optional[List[str]] = Field(None, min_items=2, max_items=6)
    dining_style: Optional[DiningStyleEnum] = None
    
    # Chef Settings
    is_chef: Optional[bool] = None
    chef_availability: Optional[Dict[str, Any]] = None
    
    # Special Needs
    has_special_needs: Optional[bool] = None
    special_needs_details: Optional[Dict[str, Any]] = None
    
    # Pets
    has_pets: Optional[bool] = None
    pets_info: Optional[Dict[str, Any]] = None
    
    # Religion and Festivals
    religion: Optional[str] = None
    festival_preferences: Optional[Dict[str, Any]] = None
    
    # Refrigeration
    has_refrigeration: Optional[bool] = None
    
    # Meal Generation Preferences
    meal_generation_criteria: Optional[List[str]] = None
    meal_timing_preference: Optional[str] = Field(None, pattern=r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    
    # Office Meals
    needs_office_meals: Optional[bool] = None
    office_meal_preferences: Optional[Dict[str, Any]] = None


class ProfileCompletion(BaseModel):
    """Mandatory profile completion schema"""
    
    # Required Personal Information
    phone: str = Field(..., min_length=10, max_length=15)
    country_code: str = Field(..., min_length=1, max_length=5)
    height: float = Field(..., gt=0, le=300)  # in cm
    weight: float = Field(..., gt=0, le=500)  # in kg
    age: int = Field(..., gt=0, le=120)
    gender: GenderEnum
    
    # Required Address Details
    current_postal_code: str = Field(..., min_length=3, max_length=20)
    current_city: str = Field(..., min_length=2, max_length=100)
    current_country: str = Field(..., min_length=2, max_length=100)
    
    native_address: str = Field(..., min_length=10)
    native_postal_code: str = Field(..., min_length=3, max_length=20)
    native_city: str = Field(..., min_length=2, max_length=100)
    native_country: str = Field(..., min_length=2, max_length=100)
    
    # Required Preferences
    cuisines: List[str] = Field(..., min_items=2, max_items=6)
    
    # Family Settings
    is_family_account: bool = False
    family_name: Optional[str] = None
    
    @validator('preferred_meats')
    def validate_meats_for_diet(cls, v, values):
        """Validate meat preferences for non-vegetarian diet"""
        if values.get('diet') == DietEnum.NON_VEGETARIAN and not v:
            raise ValueError("Meat preferences are required for non-vegetarian diet")
        return v
    
    @validator('family_name')
    def validate_family_name(cls, v, values):
        """Validate family name for family accounts"""
        if values.get('is_family_account') and not v:
            raise ValueError("Family name is required for family accounts")
        return v


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        """Validate password confirmation"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v
