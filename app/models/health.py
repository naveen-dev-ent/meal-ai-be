from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class HealthCondition(Base):
    """Normalized health conditions lookup table"""
    __tablename__ = "health_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # chronic, acute, dietary, etc.
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VitaminDeficiency(Base):
    """Normalized vitamin deficiencies lookup table"""
    __tablename__ = "vitamin_deficiencies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # B12, D3, Iron, etc.
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserHealthCondition(Base):
    """Junction table for user health conditions"""
    __tablename__ = "user_health_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    health_condition_id = Column(Integer, ForeignKey("health_conditions.id"), nullable=False)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    diagnosed_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Soft delete (user can disable/enable conditions)
    is_active = Column(Boolean, default=True)
    
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
    
    # Soft delete (user can disable/enable deficiencies)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="vitamin_deficiencies")
    vitamin_deficiency = relationship("VitaminDeficiency")
