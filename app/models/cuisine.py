from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


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
    name = Column(String(50), unique=True, nullable=False)  # chicken, beef, lamb, fish, etc.
    category = Column(String(30), nullable=False)  # poultry, red_meat, seafood, etc.
    description = Column(Text, nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserCuisine(Base):
    """Junction table for user cuisine preferences"""
    __tablename__ = "user_cuisines"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cuisine_id = Column(Integer, ForeignKey("cuisines.id"), nullable=False)
    preference_level = Column(String(20), nullable=False)  # mandatory, preferred, optional
    
    # Soft delete (user can disable/enable preferences)
    is_active = Column(Boolean, default=True)
    
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
    
    # Soft delete (user can disable/enable preferences)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meat_preferences")
    meat_type = relationship("MeatType")
