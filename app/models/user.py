from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    TRANSGENDER = "transgender"
    OTHER = "other"


class DietEnum(str, enum.Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    EGGETARIAN = "eggetarian"
    NON_VEGETARIAN = "non_vegetarian"


class DiningStyleEnum(str, enum.Enum):
    FIVE_STAR = "5_star"
    STREET_SIDE = "street_side"
    OTHER = "other"


class PetTypeEnum(str, enum.Enum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    FISH = "fish"
    RABBIT = "rabbit"
    OTHER = "other"


# Normalized lookup tables
class Cuisine(Base):
    """Normalized cuisine lookup table"""
    __tablename__ = "cuisines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    region = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MeatType(Base):
    """Normalized meat types lookup table"""
    __tablename__ = "meat_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    category = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HealthCondition(Base):
    """Normalized health conditions lookup table"""
    __tablename__ = "health_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VitaminDeficiency(Base):
    """Normalized vitamin deficiencies lookup table"""
    __tablename__ = "vitamin_deficiencies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MealStyle(Base):
    """Normalized meal styles lookup table"""
    __tablename__ = "meal_styles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SpecialNeed(Base):
    """Normalized special needs lookup table"""
    __tablename__ = "special_needs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Festival(Base):
    """Normalized festivals lookup table"""
    __tablename__ = "festivals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    religion = Column(String(50), nullable=True)
    region = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MealGenerationCriteria(Base):
    """Normalized meal generation criteria"""
    __tablename__ = "meal_generation_criteria"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Junction tables for many-to-many relationships
class UserAddress(Base):
    """Junction table for user-address relationships"""
    __tablename__ = "user_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    address_type = Column(String(20), nullable=False)  # current, native, billing, shipping
    is_primary = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_addresses")
    address = relationship("Address")


class UserCuisine(Base):
    """Junction table for user cuisine preferences"""
    __tablename__ = "user_cuisines"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cuisine_id = Column(Integer, ForeignKey("cuisines.id"), nullable=False)
    preference_level = Column(String(20), nullable=False)  # mandatory, preferred, optional
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_cuisines")
    cuisine = relationship("Cuisine")


class UserMeatPreference(Base):
    """Junction table for user meat preferences"""
    __tablename__ = "user_meat_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meat_type_id = Column(Integer, ForeignKey("meat_types.id"), nullable=False)
    preference_level = Column(String(20), nullable=False)  # love, like, neutral, dislike
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meat_preferences")
    meat_type = relationship("MeatType")


class UserHealthCondition(Base):
    """Junction table for user health conditions"""
    __tablename__ = "user_health_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    health_condition_id = Column(Integer, ForeignKey("health_conditions.id"), nullable=False)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    diagnosed_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="health_conditions")
    health_condition = relationship("HealthCondition")


class UserVitaminDeficiency(Base):
    """Junction table for user vitamin deficiencies"""
    __tablename__ = "user_vitamin_deficiencies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vitamin_deficiency_id = Column(Integer, ForeignKey("vitamin_deficiencies.id"), nullable=False)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    diagnosed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="vitamin_deficiencies")
    vitamin_deficiency = relationship("VitaminDeficiency")


class UserMealStyle(Base):
    """Junction table for user meal style preferences"""
    __tablename__ = "user_meal_styles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_style_id = Column(Integer, ForeignKey("meal_styles.id"), nullable=False)
    preference_level = Column(String(20), nullable=False)  # love, like, neutral, avoid
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meal_style_preferences")
    meal_style = relationship("MealStyle")


class ChefAvailability(Base):
    """Normalized chef availability schedule"""
    __tablename__ = "chef_availability"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chef_schedules")


class UserSpecialNeed(Base):
    """Junction table for user special needs"""
    __tablename__ = "user_special_needs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    special_need_id = Column(Integer, ForeignKey("special_needs.id"), nullable=False)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="special_needs")
    special_need = relationship("SpecialNeed")


class Pet(Base):
    """Normalized pets table"""
    __tablename__ = "pets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    pet_type = Column(Enum(PetTypeEnum), nullable=False)
    breed = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)  # in kg
    
    # Special dietary needs
    has_special_diet = Column(Boolean, default=False)
    dietary_restrictions = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="pets")


class UserFestivalPreference(Base):
    """Junction table for user festival preferences"""
    __tablename__ = "user_festival_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False)
    preference_level = Column(String(20), nullable=False)  # celebrate, observe, ignore
    include_traditional_foods = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="festival_preferences")
    festival = relationship("Festival")


class UserMealCriteria(Base):
    """Junction table for user meal generation criteria"""
    __tablename__ = "user_meal_criteria"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    criteria_id = Column(Integer, ForeignKey("meal_generation_criteria.id"), nullable=False)
    priority = Column(Integer, nullable=False, default=1)  # 1=highest priority
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meal_criteria")
    criteria = relationship("MealGenerationCriteria")


class OfficeSchedule(Base):
    """Normalized office meal schedule"""
    __tablename__ = "office_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    needs_breakfast = Column(Boolean, default=False)
    needs_lunch = Column(Boolean, default=True)
    needs_dinner = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="office_schedules")


class User(Base):
    """Normalized User table following 3NF principles"""
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication (1NF - atomic values)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    country_code = Column(String(5), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Personal Information (1NF - atomic values)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    height = Column(Float, nullable=True)  # in cm
    weight = Column(Float, nullable=True)  # in kg
    age = Column(Integer, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    
    # Basic address (simplified for signup, detailed addresses normalized separately)
    current_address = Column(Text, nullable=False)
    
    # Diet preference (atomic value)
    diet = Column(Enum(DietEnum), nullable=True)
    dining_style = Column(Enum(DiningStyleEnum), nullable=True)
    
    # Family relationship (foreign key reference)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    is_family_account = Column(Boolean, default=False)
    is_decision_maker = Column(Boolean, default=False)
    is_chef = Column(Boolean, default=False)
    
    # Budget (atomic values)
    daily_budget = Column(Float, nullable=True)
    monthly_budget = Column(Float, nullable=True)
    one_time_budget = Column(Float, nullable=True)
    
    # Status flags (atomic boolean values)
    profile_completed = Column(Boolean, default=False)
    has_special_needs = Column(Boolean, default=False)
    has_pets = Column(Boolean, default=False)
    has_refrigeration = Column(Boolean, nullable=True)
    needs_office_meals = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Religion (atomic value)
    religion = Column(String(100), nullable=True)
    
    # Meal timing preference (atomic value)
    meal_timing_preference = Column(String(10), nullable=True, default="18:00")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships (2NF/3NF - separate tables for multi-valued attributes)
    family = relationship("Family", back_populates="members")
    user_addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    health_conditions = relationship("UserHealthCondition", back_populates="user", cascade="all, delete-orphan")
    vitamin_deficiencies = relationship("UserVitaminDeficiency", back_populates="user", cascade="all, delete-orphan")
    user_cuisines = relationship("UserCuisine", back_populates="user", cascade="all, delete-orphan")
    meat_preferences = relationship("UserMeatPreference", back_populates="user", cascade="all, delete-orphan")
    meal_style_preferences = relationship("UserMealStyle", back_populates="user", cascade="all, delete-orphan")
    chef_schedules = relationship("ChefAvailability", back_populates="user", cascade="all, delete-orphan")
    special_needs = relationship("UserSpecialNeed", back_populates="user", cascade="all, delete-orphan")
    pets = relationship("Pet", back_populates="user", cascade="all, delete-orphan")
    festival_preferences = relationship("UserFestivalPreference", back_populates="user", cascade="all, delete-orphan")
    meal_criteria = relationship("UserMealCriteria", back_populates="user", cascade="all, delete-orphan")
    office_schedules = relationship("OfficeSchedule", back_populates="user", cascade="all, delete-orphan")
    
    # Existing relationships
    stocks = relationship("Stock", back_populates="user", foreign_keys="[Stock.user_id]")
    meals = relationship("Meal", back_populates="user", foreign_keys="[Meal.user_id]")
    health_records = relationship("HealthRecord", back_populates="user")
    snacks = relationship("Snack", back_populates="user", foreign_keys="[Snack.user_id]")
    meal_feedbacks = relationship("MealFeedback", back_populates="user")
    vacations = relationship("Vacation", back_populates="user")


class FamilyMemberPriority(Base):
    """Normalized family member priority rankings"""
    __tablename__ = "family_member_priorities"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    priority_rank = Column(Integer, nullable=False)  # 1=highest priority
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    family = relationship("Family", back_populates="member_priorities")
    user = relationship("User")


class FamilyMealPartition(Base):
    """Normalized family meal portion ratios"""
    __tablename__ = "family_meal_partitions"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portion_ratio = Column(Float, nullable=False, default=1.0)  # 1.0 = normal portion
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    family = relationship("Family", back_populates="meal_partitions")
    user = relationship("User")


class FamilyGuestPreference(Base):
    """Normalized family guest meal preferences"""
    __tablename__ = "family_guest_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    preference_type = Column(String(50), nullable=False)  # cuisine, diet, spice_level, etc.
    preference_value = Column(String(100), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    family = relationship("Family", back_populates="guest_preferences")


class Family(Base):
    """Normalized Family table"""
    __tablename__ = "families"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    meal_frequency = Column(Integer, nullable=False, default=3)
    
    # Guest Management (atomic values only)
    guest_count = Column(Integer, default=0)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("User", back_populates="family")
    member_priorities = relationship("FamilyMemberPriority", back_populates="family", cascade="all, delete-orphan")
    meal_partitions = relationship("FamilyMealPartition", back_populates="family", cascade="all, delete-orphan")
    guest_preferences = relationship("FamilyGuestPreference", back_populates="family", cascade="all, delete-orphan")
    meals = relationship("Meal", back_populates="family")
    stocks = relationship("Stock", back_populates="family")
    snacks = relationship("Snack", back_populates="family")
    guests = relationship("Guest", back_populates="family")
    vacations = relationship("Vacation", back_populates="family")


class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    
    # Item Details
    item_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # Enhanced categories from StockCategoryEnum
    subcategory = Column(String(100), nullable=True)
    brand = Column(String(100), nullable=True)
    weight = Column(Float, nullable=False)  # in kg
    unit = Column(String(10), nullable=False, default="kg")
    
    # Nutritional Information
    calories_per_100g = Column(Float, nullable=True)
    protein_per_100g = Column(Float, nullable=True)
    carbs_per_100g = Column(Float, nullable=True)
    fat_per_100g = Column(Float, nullable=True)
    fiber_per_100g = Column(Float, nullable=True)
    
    # Stock Management
    current_quantity = Column(Float, nullable=False)
    minimum_quantity = Column(Float, nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    is_perishable = Column(Boolean, default=False)
    
    # Pricing
    price_per_unit = Column(Float, nullable=True)
    currency = Column(String(3), default="USD")
    
    # Enhanced Categorization
    is_special_care_item = Column(Boolean, default=False)
    special_care_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    special_care_types = Column(Text, nullable=True)  # JSON array of SpecialCareTypeEnum
    
    # Pet Food
    is_pet_food = Column(Boolean, default=False)
    pet_type = Column(String(50), nullable=True)  # dog, cat, bird, etc.
    
    # Storage & Priority
    storage_type = Column(String(50), default="pantry")  # StorageTypeEnum
    priority_level = Column(String(20), default="important")  # StockPriorityEnum
    requires_refrigeration = Column(Boolean, default=False)
    refrigeration_temperature = Column(Float, nullable=True)  # in Celsius
    
    # Health & Diet
    is_organic = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_diabetic_friendly = Column(Boolean, default=False)
    allergen_info = Column(Text, nullable=True)  # JSON array of allergens
    
    # Family Assignment
    assignment_type = Column(String(20), default="shared")  # exclusive, preferred, shared
    assignment_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="stocks", foreign_keys=[user_id])
    family = relationship("Family", back_populates="stocks")
    movements = relationship("StockMovement", back_populates="stock")
    alerts = relationship("StockAlert", back_populates="stock")


class StockMovement(Base):
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity_change = Column(Float, nullable=False)  # positive for addition, negative for consumption
    movement_type = Column(String(20), nullable=False)  # addition, consumption, adjustment, expiry, damage
    reason = Column(String(255), nullable=True)
    date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    notes = Column(Text, nullable=True)

    # Relationships
    stock = relationship("Stock", back_populates="movements")


class StockAlert(Base):
    __tablename__ = "stock_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    alert_type = Column(String(20), nullable=False)  # low_stock, expiring_soon, expired, overstock
    message = Column(Text, nullable=False)
    priority = Column(String(10), nullable=False)  # low, medium, high, critical
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    stock = relationship("Stock", back_populates="alerts")
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])


class Meal(Base):
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    
    # Meal Details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    
    # Timing
    planned_date = Column(DateTime(timezone=True), nullable=False)
    planned_time = Column(String(10), nullable=False)
    
    # Nutritional Information
    total_calories = Column(Float, nullable=True)
    total_protein = Column(Float, nullable=True)
    total_carbs = Column(Float, nullable=True)
    total_fat = Column(Float, nullable=True)
    
    # Ingredients
    ingredients = Column(Text, nullable=False)  # JSON string for ingredients with quantities
    cooking_instructions = Column(Text, nullable=True)
    
    # Status
    status = Column(String(50), default="planned")  # planned, approved, cooking, completed
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Special Requirements
    is_special_care_meal = Column(Boolean, default=False)
    is_office_meal = Column(Boolean, default=False)
    is_guest_meal = Column(Boolean, default=False)
    
    # Feedback
    rating = Column(Integer, nullable=True)  # 1-5 stars
    feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meals", foreign_keys=[user_id])
    family = relationship("Family", back_populates="meals")
    feedbacks = relationship("MealFeedback", back_populates="meal")


class HealthRecord(Base):
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Health Metrics
    weight = Column(Float, nullable=True)
    blood_pressure = Column(String(20), nullable=True)
    blood_sugar = Column(Float, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    
    # Nutritional Intake
    daily_calories = Column(Float, nullable=True)
    daily_protein = Column(Float, nullable=True)
    daily_carbs = Column(Float, nullable=True)
    daily_fat = Column(Float, nullable=True)
    
    # Health Conditions
    conditions = Column(Text, nullable=True)  # JSON string for health conditions
    medications = Column(Text, nullable=True)  # JSON string for medications
    
    # Timestamps
    record_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="health_records")


class Snack(Base):
    __tablename__ = "snacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    
    # Snack Details
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # snack, dessert, juice
    description = Column(Text, nullable=True)
    
    # Timing and Frequency
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly
    preferred_time = Column(String(10), nullable=True)  # HH:MM format
    days_of_week = Column(Text, nullable=True)  # JSON string for specific days
    
    # Nutritional Information
    calories_per_serving = Column(Float, nullable=True)
    protein_per_serving = Column(Float, nullable=True)
    carbs_per_serving = Column(Float, nullable=True)
    fat_per_serving = Column(Float, nullable=True)
    
    # Special Requirements
    is_special_care = Column(Boolean, default=False)
    special_care_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="snacks", foreign_keys=[user_id])
    family = relationship("Family", back_populates="snacks")


class Guest(Base):
    __tablename__ = "guests"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    
    # Guest Details
    name = Column(String(255), nullable=True)  # Optional for anonymous guests
    guest_count = Column(Integer, nullable=False, default=1)
    
    # Meal Preferences
    meal_preferences = Column(Text, nullable=True)  # JSON string for dietary restrictions
    meal_timing = Column(String(10), nullable=True)  # HH:MM format
    
    # Visit Details
    visit_date = Column(DateTime(timezone=True), nullable=False)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, all
    duration_days = Column(Integer, default=1)
    
    # Special Requirements
    has_special_needs = Column(Boolean, default=False)
    special_needs_details = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    family = relationship("Family", back_populates="guests")


class MealFeedback(Base):
    __tablename__ = "meal_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Feedback Details
    rating = Column(Integer, nullable=False)  # 1-5 stars
    feedback_type = Column(String(20), nullable=False)  # like, dislike, comment
    comment = Column(Text, nullable=True)
    
    # Nutritional Feedback
    taste_rating = Column(Integer, nullable=True)  # 1-5 stars
    health_rating = Column(Integer, nullable=True)  # 1-5 stars
    portion_rating = Column(Integer, nullable=True)  # 1-5 stars
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    meal = relationship("Meal", back_populates="feedbacks")
    user = relationship("User", back_populates="meal_feedbacks")


class Vacation(Base):
    __tablename__ = "vacations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)
    
    # Vacation Details
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    destination = Column(String(255), nullable=True)
    
    # Meal Handling
    pause_meal_generation = Column(Boolean, default=True)
    log_external_meals = Column(Boolean, default=False)
    
    # External Meal Logging
    external_meals = Column(Text, nullable=True)  # JSON string for logged meals
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="vacations")
    family = relationship("Family", back_populates="vacations")
