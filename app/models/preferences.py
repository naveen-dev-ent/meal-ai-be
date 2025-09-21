from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MealStyle(Base):
    """Normalized meal styles lookup table"""
    __tablename__ = "meal_styles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # healthy, junk, spicy, tasty
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserMealStyle(Base):
    """Junction table for user meal style preferences"""
    __tablename__ = "user_meal_styles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_style_id = Column(Integer, ForeignKey("meal_styles.id"), nullable=False)
    preference_level = Column(String(20), nullable=False)  # love, like, neutral, avoid
    
    # Soft delete (user can disable/enable preferences)
    is_active = Column(Boolean, default=True)
    
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


class SpecialNeed(Base):
    """Normalized special needs lookup table"""
    __tablename__ = "special_needs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # dietary, physical, medical, etc.
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserSpecialNeed(Base):
    """Junction table for user special needs"""
    __tablename__ = "user_special_needs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    special_need_id = Column(Integer, ForeignKey("special_needs.id"), nullable=False)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    notes = Column(Text, nullable=True)
    
    # Soft delete (user can disable/enable special needs)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="special_needs")
    special_need = relationship("SpecialNeed")
