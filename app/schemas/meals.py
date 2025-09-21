from pydantic import BaseModel, validator, Field
from typing import Optional, List
from enum import Enum


class MealTypeEnum(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class MealStatusEnum(str, Enum):
    PLANNED = "planned"
    APPROVED = "approved"
    COOKING = "cooking"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FeedbackTypeEnum(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    COMMENT = "comment"


# Base Meal Schema
class MealBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    meal_type: MealTypeEnum
    
    # Timing
    planned_date: date
    planned_time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    
    # Nutritional Information
    total_calories: Optional[float] = Field(None, gt=0)
    total_protein: Optional[float] = Field(None, gt=0)
    total_carbs: Optional[float] = Field(None, gt=0)
    total_fat: Optional[float] = Field(None, gt=0)
    
    # Ingredients
    ingredients: List[Dict[str, Any]] = Field(..., min_items=1)  # ingredient details with quantities
    
    # Cooking Instructions
    cooking_instructions: Optional[str] = None
    
    # Special Requirements
    is_special_care_meal: bool = False
    is_office_meal: bool = False
    is_guest_meal: bool = False

    @validator('ingredients')
    def validate_ingredients(cls, v):
        required_fields = ['name', 'quantity', 'unit']
        for ingredient in v:
            if not all(field in ingredient for field in required_fields):
                raise ValueError(f'Each ingredient must have: {required_fields}')
        return v


# Meal Create Schema
class MealCreate(MealBase):
    user_id: Optional[int] = None
    family_id: Optional[int] = None


# Meal Update Schema
class MealUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    meal_type: Optional[MealTypeEnum] = None
    planned_date: Optional[date] = None
    planned_time: Optional[str] = Field(None, pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    total_calories: Optional[float] = Field(None, gt=0)
    total_protein: Optional[float] = Field(None, gt=0)
    total_carbs: Optional[float] = Field(None, gt=0)
    total_fat: Optional[float] = Field(None, gt=0)
    ingredients: Optional[List[Dict[str, Any]]] = None
    cooking_instructions: Optional[str] = None
    is_special_care_meal: Optional[bool] = None
    is_office_meal: Optional[bool] = None
    is_guest_meal: Optional[bool] = None


# Meal Response Schema
class MealResponse(MealBase):
    id: int
    user_id: Optional[int]
    family_id: Optional[int]
    status: MealStatusEnum
    is_approved: bool
    approved_by: Optional[int]
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Meal List Schema
class MealList(BaseModel):
    id: int
    name: str
    meal_type: MealTypeEnum
    planned_date: date
    planned_time: str
    status: MealStatusEnum
    is_approved: bool
    total_calories: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


# Meal Approval Schema
class MealApproval(BaseModel):
    is_approved: bool
    notes: Optional[str] = None


# Meal Generation Request Schema
class MealGenerationRequest(BaseModel):
    generation_date: date
    meal_types: List[MealTypeEnum] = Field(..., min_items=1)
    user_id: Optional[int] = None
    family_id: Optional[int] = None
    
    # Generation Criteria
    use_stock: bool = True
    use_region_based: bool = True
    use_native_based: bool = True
    prioritize_expiry: bool = True
    
    # Special Requirements
    include_guests: bool = False
    guest_count: int = 0
    is_office_meal: bool = False
    special_dietary_needs: Optional[List[str]] = None


# Meal Generation Response Schema
class MealGenerationResponse(BaseModel):
    meals: List[MealResponse]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    estimated_cost: Optional[float]
    stock_items_used: List[str]
    items_to_purchase: List[str]


# Meal Feedback Schema
class MealFeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback_type: FeedbackTypeEnum
    comment: Optional[str] = None
    
    # Nutritional Feedback
    taste_rating: Optional[int] = Field(None, ge=1, le=5)
    health_rating: Optional[int] = Field(None, ge=1, le=5)
    portion_rating: Optional[int] = Field(None, ge=1, le=5)


class MealFeedbackCreate(MealFeedbackBase):
    meal_id: int


class MealFeedbackUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_type: Optional[FeedbackTypeEnum] = None
    comment: Optional[str] = None
    taste_rating: Optional[int] = Field(None, ge=1, le=5)
    health_rating: Optional[int] = Field(None, ge=1, le=5)
    portion_rating: Optional[int] = Field(None, ge=1, le=5)


class MealFeedbackResponse(MealFeedbackBase):
    id: int
    meal_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Meal Plan Schema (for weekly/daily planning)
class MealPlan(BaseModel):
    date: date
    meals: List[MealResponse]
    total_nutrition: Dict[str, float]
    shopping_list: List[str]
    estimated_cost: float


# Meal Template Schema (for reusable meal patterns)
class MealTemplate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    meal_type: MealTypeEnum
    ingredients: List[Dict[str, Any]]
    cooking_instructions: Optional[str] = None
    nutritional_info: Optional[Dict[str, float]] = None
    tags: List[str] = []
    cuisine: Optional[str] = None
    difficulty_level: Optional[str] = None
    cooking_time_minutes: Optional[int] = None
    servings: Optional[int] = Field(None, gt=0)


class MealTemplateCreate(MealTemplate):
    pass


class MealTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    meal_type: Optional[MealTypeEnum] = None
    ingredients: Optional[List[Dict[str, Any]]] = None
    cooking_instructions: Optional[str] = None
    nutritional_info: Optional[Dict[str, float]] = None
    tags: Optional[List[str]] = None
    cuisine: Optional[str] = None
    difficulty_level: Optional[str] = None
    cooking_time_minutes: Optional[int] = Field(None, gt=0)
    servings: Optional[int] = Field(None, gt=0)


class MealTemplateResponse(MealTemplate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Meal History Schema
class MealHistory(BaseModel):
    date: date
    meals: List[MealResponse]
    total_calories: float
    average_rating: Optional[float]
    feedback_count: int


# Meal Analytics Schema
class MealAnalytics(BaseModel):
    total_meals: int
    average_rating: float
    favorite_meals: List[str]
    least_favorite_meals: List[str]
    nutritional_totals: Dict[str, float]
    cost_analysis: Dict[str, float]
    meal_type_distribution: Dict[str, int]
