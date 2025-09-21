from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MealGenerationCriteria(Base):
    """Normalized meal generation criteria"""
    __tablename__ = "meal_generation_criteria"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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