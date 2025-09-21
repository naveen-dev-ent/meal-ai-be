from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
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


# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    country_code: str = Field(..., min_length=1, max_length=5)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    height: float = Field(..., gt=0, le=300)  # cm
    weight: float = Field(..., gt=0, le=500)  # kg
    age: int = Field(..., gt=0, le=150)
    gender: GenderEnum
    
    # Addresses
    current_address: str = Field(..., min_length=5)
    current_postal_code: str = Field(..., min_length=3, max_length=20)
    current_city: str = Field(..., min_length=2, max_length=100)
    current_country: str = Field(..., min_length=2, max_length=100)
    
    native_address: str = Field(..., min_length=5)
    native_postal_code: str = Field(..., min_length=3, max_length=20)
    native_city: str = Field(..., min_length=2, max_length=100)
    native_country: str = Field(..., min_length=2, max_length=100)
    
    # Budget
    daily_budget: Optional[float] = Field(None, gt=0)
    monthly_budget: Optional[float] = Field(None, gt=0)
    one_time_budget: Optional[float] = Field(None, gt=0)
    
    # Health and Diet
    diet: DietEnum
    preferred_meats: Optional[List[str]] = None
    health_conditions: Optional[List[str]] = None
    vitamin_deficiencies: Optional[List[str]] = None
    
    # Preferences
    meal_styles: Optional[List[str]] = None
    cuisines: List[str] = Field(..., min_items=2, max_items=6)
    dining_style: Optional[DiningStyleEnum] = None
    
    # Family Settings
    is_family_account: bool = False
    is_decision_maker: bool = False
    is_chef: bool = False
    chef_availability: Optional[Dict[str, Any]] = None
    
    # Special Needs
    has_special_needs: bool = False
    special_needs_details: Optional[str] = None
    
    # Pets
    has_pets: bool = False
    pets_info: Optional[Dict[str, Any]] = None
    
    # Religion and Festivals
    religion: Optional[str] = None
    festival_preferences: Optional[Dict[str, Any]] = None
    
    # Refrigeration
    has_refrigeration: Optional[bool] = None
    
    # Meal Generation Preferences
    meal_generation_criteria: List[str] = Field(..., min_items=1)
    meal_timing_preference: str = Field(default="18:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    
    # Office Meals
    needs_office_meals: bool = False
    office_meal_preferences: Optional[Dict[str, Any]] = None

    @validator('preferred_meats')
    def validate_preferred_meats(cls, v, values):
        if v and values.get('diet') != DietEnum.NON_VEGETARIAN:
            raise ValueError('Preferred meats can only be set for non-vegetarian diets')
        return v

    @validator('cuisines')
    def validate_cuisines(cls, v):
        if len(v) < 2:
            raise ValueError('At least 2 cuisines must be selected')
        return v

    @validator('meal_generation_criteria')
    def validate_meal_generation_criteria(cls, v):
        valid_criteria = ['stock_based', 'region_based', 'native_based']
        if not all(criteria in valid_criteria for criteria in v):
            raise ValueError(f'Invalid meal generation criteria. Must be one of: {valid_criteria}')
        return v


# User Create Schema
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


# User Update Schema
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    height: Optional[float] = Field(None, gt=0, le=300)
    weight: Optional[float] = Field(None, gt=0, le=500)
    age: Optional[int] = Field(None, gt=0, le=150)
    gender: Optional[GenderEnum] = None
    
    # Addresses
    current_address: Optional[str] = Field(None, min_length=5)
    current_postal_code: Optional[str] = Field(None, min_length=3, max_length=20)
    current_city: Optional[str] = Field(None, min_length=2, max_length=100)
    current_country: Optional[str] = Field(None, min_length=2, max_length=100)
    
    native_address: Optional[str] = Field(None, min_length=5)
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
    cuisines: Optional[List[str]] = None
    dining_style: Optional[DiningStyleEnum] = None
    
    # Family Settings
    is_family_account: Optional[bool] = None
    is_decision_maker: Optional[bool] = None
    is_chef: Optional[bool] = None
    chef_availability: Optional[Dict[str, Any]] = None
    
    # Special Needs
    has_special_needs: Optional[bool] = None
    special_needs_details: Optional[str] = None
    
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
    meal_timing_preference: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    
    # Office Meals
    needs_office_meals: Optional[bool] = None
    office_meal_preferences: Optional[Dict[str, Any]] = None


# User Response Schema
class UserResponse(BaseModel):
    id: int
    email: str
    phone: str
    country_code: str
    first_name: str
    last_name: str
    height: float
    weight: float
    age: int
    gender: GenderEnum
    
    # Addresses
    current_address: str
    current_postal_code: str
    current_city: str
    current_country: str
    
    native_address: str
    native_postal_code: str
    native_city: str
    native_country: str
    
    # Budget
    daily_budget: Optional[float]
    monthly_budget: Optional[float]
    one_time_budget: Optional[float]
    
    # Health and Diet
    diet: DietEnum
    preferred_meats: Optional[List[str]]
    health_conditions: Optional[List[str]]
    vitamin_deficiencies: Optional[List[str]]
    
    # Preferences
    meal_styles: Optional[List[str]]
    cuisines: List[str]
    dining_style: Optional[DiningStyleEnum]
    
    # Family Settings
    is_family_account: bool
    family_id: Optional[int]
    is_decision_maker: bool
    is_chef: bool
    chef_availability: Optional[Dict[str, Any]]
    
    # Special Needs
    has_special_needs: bool
    special_needs_details: Optional[str]
    
    # Pets
    has_pets: bool
    pets_info: Optional[Dict[str, Any]]
    
    # Religion and Festivals
    religion: Optional[str]
    festival_preferences: Optional[Dict[str, Any]]
    
    # Refrigeration
    has_refrigeration: Optional[bool]
    
    # Meal Generation Preferences
    meal_generation_criteria: List[str]
    meal_timing_preference: str
    
    # Office Meals
    needs_office_meals: bool
    office_meal_preferences: Optional[Dict[str, Any]]
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# User List Schema
class UserList(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    is_family_account: bool
    family_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# User Profile Schema (for dashboard display)
class UserProfile(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    height: float
    weight: float
    age: int
    gender: GenderEnum
    diet: DietEnum
    has_special_needs: bool
    has_pets: bool
    is_family_account: bool
    family_id: Optional[int]
    is_decision_maker: bool
    is_chef: bool
    created_at: datetime

    class Config:
        from_attributes = True
