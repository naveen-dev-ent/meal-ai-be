from pydantic import BaseModel, validator, Field
from typing import Optional, List
from enum import Enum


class MealTypeEnum(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


# Base Family Schema
class FamilyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    meal_frequency: int = Field(..., ge=1, le=6)  # meals per day
    meal_timings: Dict[str, str] = Field(..., min_items=1)  # meal type -> time
    
    # Meal Partitioning
    meal_partitioning: Optional[Dict[str, float]] = None  # member_id -> ratio
    
    # Priority Settings
    member_priorities: Optional[List[int]] = None  # ordered list of member IDs by priority
    
    # Guest Management
    guest_count: int = Field(default=0, ge=0)
    guest_meal_preferences: Optional[Dict[str, Any]] = None

    @validator('meal_timings')
    def validate_meal_timings(cls, v):
        valid_meals = ['breakfast', 'lunch', 'dinner', 'snack']
        if not all(meal in valid_meals for meal in v.keys()):
            raise ValueError(f'Invalid meal types. Must be one of: {valid_meals}')
        
        # Validate time format HH:MM
        import re
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not all(re.match(time_pattern, time) for time in v.values()):
            raise ValueError('Invalid time format. Use HH:MM format')
        
        return v

    @validator('meal_partitioning')
    def validate_meal_partitioning(cls, v):
        if v:
            total_ratio = sum(v.values())
            if abs(total_ratio - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError('Meal partitioning ratios must sum to 1.0')
        return v


# Family Create Schema
class FamilyCreate(FamilyBase):
    pass


# Family Update Schema
class FamilyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    meal_frequency: Optional[int] = Field(None, ge=1, le=6)
    meal_timings: Optional[Dict[str, str]] = None
    meal_partitioning: Optional[Dict[str, float]] = None
    member_priorities: Optional[List[int]] = None
    guest_count: Optional[int] = Field(None, ge=0)
    guest_meal_preferences: Optional[Dict[str, Any]] = None


# Family Response Schema
class FamilyResponse(FamilyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Family Member Schema
class FamilyMember(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    is_decision_maker: bool
    is_chef: bool
    chef_availability: Optional[Dict[str, Any]]
    has_special_needs: bool
    has_pets: bool
    diet: str
    age: int
    gender: str
    created_at: datetime

    class Config:
        from_attributes = True


# Family Detail Schema (with members)
class FamilyDetail(FamilyResponse):
    members: List[FamilyMember]
    total_members: int

    class Config:
        from_attributes = True


# Family List Schema
class FamilyList(BaseModel):
    id: int
    name: str
    meal_frequency: int
    total_members: int
    created_at: datetime

    class Config:
        from_attributes = True


# Guest Schema
class GuestBase(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    guest_count: int = Field(..., ge=1, le=20)
    meal_preferences: Optional[Dict[str, Any]] = None
    meal_timing: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    visit_date: date
    meal_type: str = Field(..., pattern=r"^(breakfast|lunch|dinner|all)$")
    duration_days: int = Field(default=1, ge=1, le=30)
    has_special_needs: bool = False
    special_needs_details: Optional[str] = None


class GuestCreate(GuestBase):
    family_id: int


class GuestUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    guest_count: Optional[int] = Field(None, ge=1, le=20)
    meal_preferences: Optional[Dict[str, Any]] = None
    meal_timing: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    visit_date: Optional[date] = None
    meal_type: Optional[str] = Field(None, pattern=r"^(breakfast|lunch|dinner|all)$")
    duration_days: Optional[int] = Field(None, ge=1, le=30)
    has_special_needs: Optional[bool] = None
    special_needs_details: Optional[str] = None


class GuestResponse(GuestBase):
    id: int
    family_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Meal Partitioning Schema
class MealPartitioning(BaseModel):
    member_id: int
    ratio: float = Field(..., gt=0, le=1)
    meal_types: List[str] = Field(..., min_items=1)  # breakfast, lunch, dinner, snack


# Chef Availability Schema
class ChefAvailability(BaseModel):
    days_of_week: List[str] = Field(..., min_items=1)  # Monday, Tuesday, etc.
    meal_types: List[str] = Field(..., min_items=1)  # breakfast, lunch, dinner, snack
    start_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    is_available: bool = True
    notes: Optional[str] = None

    @validator('days_of_week')
    def validate_days(cls, v):
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if not all(day in valid_days for day in v):
            raise ValueError(f'Invalid days. Must be one of: {valid_days}')
        return v

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if 'start_time' in values:
            from datetime import datetime
            start = datetime.strptime(values['start_time'], '%H:%M')
            end = datetime.strptime(v, '%H:%M')
            if end <= start:
                raise ValueError('End time must be after start time')
        return v


# Family Settings Update Schema
class FamilySettingsUpdate(BaseModel):
    meal_frequency: Optional[int] = Field(None, ge=1, le=6)
    meal_timings: Optional[Dict[str, str]] = None
    meal_partitioning: Optional[Dict[str, float]] = None
    member_priorities: Optional[List[int]] = None
    guest_meal_preferences: Optional[Dict[str, Any]] = None
