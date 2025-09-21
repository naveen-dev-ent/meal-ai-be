from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import date, datetime
from .stock_categories import (
    StockCategoryEnum,
    PetFoodTypeEnum,
    SpecialCareTypeEnum,
    StorageTypeEnum,
    StockPriorityEnum,
    AssignmentTypeEnum
)


# Enhanced Stock Schemas with Categorization


class UnitEnum(str, Enum):
    KG = "kg"
    G = "g"
    L = "l"
    ML = "ml"
    PCS = "pcs"
    PACKS = "packs"
    BOTTLES = "bottles"
    CANS = "cans"


# Base Stock Schema with Enhanced Categorization
class StockBase(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=255)
    category: StockCategoryEnum
    subcategory: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    weight: float = Field(..., gt=0)
    unit: UnitEnum = UnitEnum.KG
    
    # Nutritional Information (per 100g)
    calories_per_100g: Optional[float] = Field(None, ge=0)
    protein_per_100g: Optional[float] = Field(None, ge=0)
    carbs_per_100g: Optional[float] = Field(None, ge=0)
    fat_per_100g: Optional[float] = Field(None, ge=0)
    fiber_per_100g: Optional[float] = Field(None, ge=0)
    
    # Stock Management
    current_quantity: float = Field(..., gt=0)
    minimum_quantity: float = Field(..., ge=0)
    expiry_date: Optional[date] = None
    is_perishable: bool = False
    
    # Pricing
    price_per_unit: Optional[float] = Field(None, ge=0)
    currency: str = "USD"
    
    # Enhanced Categorization
    is_special_care_item: bool = False
    special_care_types: Optional[List[SpecialCareTypeEnum]] = None
    
    # Pet Food
    is_pet_food: bool = False
    pet_type: Optional[PetFoodTypeEnum] = None
    
    # Storage & Priority
    storage_type: StorageTypeEnum = StorageTypeEnum.PANTRY
    priority_level: StockPriorityEnum = StockPriorityEnum.IMPORTANT
    requires_refrigeration: bool = False
    refrigeration_temperature: Optional[float] = Field(None, ge=-50, le=50)  # Celsius
    
    # Health & Diet
    is_organic: bool = False
    is_gluten_free: bool = False
    is_vegan: bool = False
    is_diabetic_friendly: bool = False
    allergen_info: Optional[List[str]] = None
    
    # Family Assignment
    assignment_type: AssignmentTypeEnum = AssignmentTypeEnum.SHARED
    assignment_notes: Optional[str] = None

    @validator('minimum_quantity')
    def validate_minimum_quantity(cls, v, values):
        if 'current_quantity' in values and v > values['current_quantity']:
            raise ValueError('Minimum quantity cannot be greater than current quantity')
        return v

    @validator('expiry_date')
    def validate_expiry_date(cls, v):
        if v and v < date.today():
            raise ValueError('Expiry date cannot be in the past')
        return v


# Stock Create Schema
class StockCreate(StockBase):
    user_id: Optional[int] = None
    family_id: Optional[int] = None
    special_care_user_id: Optional[int] = None


# Stock Update Schema
class StockUpdate(BaseModel):
    item_name: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[StockCategoryEnum] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, gt=0)
    unit: Optional[UnitEnum] = None
    calories_per_100g: Optional[float] = Field(None, ge=0)
    protein_per_100g: Optional[float] = Field(None, ge=0)
    carbs_per_100g: Optional[float] = Field(None, ge=0)
    fat_per_100g: Optional[float] = Field(None, ge=0)
    fiber_per_100g: Optional[float] = Field(None, ge=0)
    current_quantity: Optional[float] = Field(None, gt=0)
    minimum_quantity: Optional[float] = Field(None, ge=0)
    expiry_date: Optional[date] = None
    is_perishable: Optional[bool] = None
    price_per_unit: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    
    # Enhanced Categorization
    is_special_care_item: Optional[bool] = None
    special_care_types: Optional[List[SpecialCareTypeEnum]] = None
    special_care_user_id: Optional[int] = None
    
    # Pet Food
    is_pet_food: Optional[bool] = None
    pet_type: Optional[PetFoodTypeEnum] = None
    
    # Storage & Priority
    storage_type: Optional[StorageTypeEnum] = None
    priority_level: Optional[StockPriorityEnum] = None
    requires_refrigeration: Optional[bool] = None
    refrigeration_temperature: Optional[float] = Field(None, ge=-50, le=50)
    
    # Health & Diet
    is_organic: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_diabetic_friendly: Optional[bool] = None
    allergen_info: Optional[List[str]] = None
    
    # Family Assignment
    assignment_type: Optional[AssignmentTypeEnum] = None
    assignment_notes: Optional[str] = None


# Stock Response Schema
class StockResponse(StockBase):
    id: int
    user_id: Optional[int]
    family_id: Optional[int]
    special_care_user_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Stock List Schema
class StockList(BaseModel):
    id: int
    item_name: str
    category: StockCategoryEnum
    subcategory: Optional[str]
    brand: Optional[str]
    current_quantity: float
    unit: UnitEnum
    minimum_quantity: float
    expiry_date: Optional[date]
    is_perishable: bool
    price_per_unit: Optional[float]
    
    # Enhanced Categorization
    is_special_care_item: bool
    special_care_types: Optional[List[SpecialCareTypeEnum]]
    is_pet_food: bool
    pet_type: Optional[PetFoodTypeEnum]
    storage_type: StorageTypeEnum
    priority_level: StockPriorityEnum
    requires_refrigeration: bool
    
    # Health & Diet
    is_organic: bool
    is_gluten_free: bool
    is_vegan: bool
    is_diabetic_friendly: bool
    
    # Family Assignment
    assignment_type: AssignmentTypeEnum
    created_at: datetime

    class Config:
        from_attributes = True


# Stock Movement Schema
class StockMovementCreate(BaseModel):
    stock_id: int
    quantity_change: float
    movement_type: str = Field(..., pattern=r"^(addition|consumption|adjustment|expiry|damage)$")
    movement_date: date = Field(default_factory=date.today)
    notes: Optional[str] = None
    reason: Optional[str] = None


# Stock Alert Schema
class StockAlert(BaseModel):
    stock_id: int
    alert_type: str = Field(..., pattern=r"^(low_stock|expiring_soon|expired|overstock)$")
    message: str
    priority: str = Field(..., pattern=r"^(low|medium|high|critical)$")
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None


# Stock Analytics Schema
class StockAnalytics(BaseModel):
    total_items: int
    total_value: float
    low_stock_items: int
    expiring_soon_items: int
    expired_items: int
    category_distribution: Dict[str, int]
    value_by_category: Dict[str, float]
    consumption_trends: Dict[str, float]
    expiry_risk: List[Dict[str, Any]]


# Enhanced Stock Search Schema
class StockSearch(BaseModel):
    query: Optional[str] = None
    category: Optional[StockCategoryEnum] = None
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    is_perishable: Optional[bool] = None
    requires_refrigeration: Optional[bool] = None
    
    # Enhanced Categorization Filters
    is_special_care: Optional[bool] = None
    special_care_types: Optional[List[SpecialCareTypeEnum]] = None
    is_pet_food: Optional[bool] = None
    pet_type: Optional[PetFoodTypeEnum] = None
    storage_type: Optional[StorageTypeEnum] = None
    priority_level: Optional[StockPriorityEnum] = None
    
    # Health & Diet Filters
    is_organic: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_diabetic_friendly: Optional[bool] = None
    
    # Family Assignment Filters
    assignment_type: Optional[AssignmentTypeEnum] = None
    assigned_to_user_id: Optional[int] = None
    
    # Price and Date Filters
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    expiry_before: Optional[date] = None
    expiry_after: Optional[date] = None
    low_stock_only: bool = False
    expiring_soon_only: bool = False


# Stock Import Schema (for bulk operations)
class StockImport(BaseModel):
    items: List[StockCreate]
    overwrite_existing: bool = False
    skip_duplicates: bool = True


# Stock Export Schema
class StockExport(BaseModel):
    format: str = Field(..., pattern=r"^(csv|json|excel)$")
    include_nutritional_info: bool = True
    include_pricing: bool = True
    include_timestamps: bool = False
    categories: Optional[List[StockCategoryEnum]] = None


# Stock Template Schema (for common items)
class StockTemplate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    category: StockCategoryEnum
    default_unit: UnitEnum
    default_minimum_quantity: float
    default_price: Optional[float] = None
    nutritional_info: Optional[Dict[str, float]] = None
    is_perishable: bool = False
    requires_refrigeration: bool = False
    shelf_life_days: Optional[int] = None
    tags: List[str] = []


class StockTemplateCreate(StockTemplate):
    pass


class StockTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[StockCategoryEnum] = None
    default_unit: Optional[UnitEnum] = None
    default_minimum_quantity: Optional[float] = None
    default_price: Optional[float] = None
    nutritional_info: Optional[Dict[str, float]] = None
    is_perishable: Optional[bool] = None
    requires_refrigeration: Optional[bool] = None
    shelf_life_days: Optional[int] = None
    tags: Optional[List[str]] = None


class StockTemplateResponse(StockTemplate):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Stock Reconciliation Schema
class StockReconciliation(BaseModel):
    stock_id: int
    expected_quantity: float
    actual_quantity: float
    difference: float
    reason: str
    reconciliation_date: date = Field(default_factory=date.today)
    notes: Optional[str] = None
    adjusted_by: int
