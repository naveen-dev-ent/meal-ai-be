"""
Enhanced stock categorization schemas and enums for better organization.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class StockCategoryEnum(str, Enum):
    """Enhanced stock categories"""
    # Food Categories
    GRAINS_CEREALS = "grains_cereals"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    DAIRY = "dairy"
    MEAT_POULTRY = "meat_poultry"
    SEAFOOD = "seafood"
    LEGUMES = "legumes"
    NUTS_SEEDS = "nuts_seeds"
    SPICES_HERBS = "spices_herbs"
    OILS_FATS = "oils_fats"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    CONDIMENTS = "condiments"
    BAKING_INGREDIENTS = "baking_ingredients"
    
    # Special Categories
    BABY_FOOD = "baby_food"
    SENIOR_FOOD = "senior_food"
    DIABETIC_FOOD = "diabetic_food"
    GLUTEN_FREE = "gluten_free"
    ORGANIC = "organic"
    
    # Pet Categories
    DOG_FOOD = "dog_food"
    CAT_FOOD = "cat_food"
    BIRD_FOOD = "bird_food"
    FISH_FOOD = "fish_food"
    PET_TREATS = "pet_treats"
    PET_SUPPLEMENTS = "pet_supplements"
    
    # Non-Food
    CLEANING_SUPPLIES = "cleaning_supplies"
    PERSONAL_CARE = "personal_care"
    HOUSEHOLD_ITEMS = "household_items"
    MEDICAL_SUPPLIES = "medical_supplies"

class SpecialCareTypeEnum(str, Enum):
    """Types of special care requirements"""
    DIABETIC = "diabetic"
    HYPERTENSION = "hypertension"
    HEART_DISEASE = "heart_disease"
    KIDNEY_DISEASE = "kidney_disease"
    PREGNANCY = "pregnancy"
    LACTATION = "lactation"
    ELDERLY = "elderly"
    CHILD = "child"
    ALLERGY_SPECIFIC = "allergy_specific"
    WEIGHT_MANAGEMENT = "weight_management"

class StorageTypeEnum(str, Enum):
    """Storage requirements"""
    PANTRY = "pantry"
    REFRIGERATOR = "refrigerator"
    FREEZER = "freezer"
    COOL_DRY_PLACE = "cool_dry_place"
    ROOM_TEMPERATURE = "room_temperature"

class StockPriorityEnum(str, Enum):
    """Stock priority levels"""
    ESSENTIAL = "essential"
    IMPORTANT = "important"
    NICE_TO_HAVE = "nice_to_have"
    LUXURY = "luxury"

class FamilyMemberStockAssignment(BaseModel):
    """Assignment of stock to specific family members"""
    family_member_id: int
    family_member_name: str
    assignment_type: str  # "exclusive", "preferred", "shared"
    notes: Optional[str] = None

class StockCategoryInfo(BaseModel):
    """Detailed category information"""
    category: StockCategoryEnum
    subcategory: Optional[str] = None
    is_food: bool = True
    typical_shelf_life_days: Optional[int] = None
    storage_requirements: List[StorageTypeEnum] = []
    nutritional_priority: Optional[str] = None

class EnhancedStockCreate(BaseModel):
    """Enhanced stock creation with better categorization"""
    # Basic Info
    item_name: str
    category: StockCategoryEnum
    subcategory: Optional[str] = None
    brand: Optional[str] = None
    
    # Quantity & Units
    weight: float
    unit: str = "kg"
    current_quantity: float
    minimum_quantity: float
    
    # Categorization
    is_pet_food: bool = False
    pet_type: Optional[str] = None
    is_special_care_item: bool = False
    special_care_types: List[SpecialCareTypeEnum] = []
    assigned_family_members: List[FamilyMemberStockAssignment] = []
    
    # Storage & Priority
    storage_type: StorageTypeEnum = StorageTypeEnum.PANTRY
    priority_level: StockPriorityEnum = StockPriorityEnum.IMPORTANT
    
    # Nutritional & Health
    is_organic: bool = False
    is_gluten_free: bool = False
    is_vegan: bool = False
    is_diabetic_friendly: bool = False
    allergen_info: List[str] = []
    
    # Existing fields
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    fiber_per_100g: Optional[float] = None
    
    # Stock Management
    expiry_date: Optional[datetime] = None
    is_perishable: bool = False
    requires_refrigeration: bool = False
    refrigeration_temperature: Optional[float] = None
    
    # Pricing
    price_per_unit: Optional[float] = None
    currency: str = "USD"

class StockCategoryStats(BaseModel):
    """Statistics for stock categories"""
    category: StockCategoryEnum
    total_items: int
    total_value: float
    low_stock_items: int
    expiring_soon_items: int
    average_days_to_expiry: Optional[float] = None
    top_items: List[str] = []

class FamilyStockDistribution(BaseModel):
    """Stock distribution across family members"""
    family_member_id: int
    family_member_name: str
    assigned_items: int
    exclusive_items: int
    total_value: float
    categories: Dict[str, int] = {}

class StockCategoryAnalytics(BaseModel):
    """Enhanced analytics with categorization"""
    total_categories: int
    category_stats: List[StockCategoryStats]
    family_distribution: List[FamilyStockDistribution]
    pet_food_stats: Dict[str, Any]
    special_care_stats: Dict[str, Any]
    storage_distribution: Dict[StorageTypeEnum, int]
    priority_distribution: Dict[StockPriorityEnum, int]
