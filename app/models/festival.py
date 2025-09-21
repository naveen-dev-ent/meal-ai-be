from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


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


class FestivalFood(Base):
    """Normalized festival foods lookup table"""
    __tablename__ = "festival_foods"
    
    id = Column(Integer, primary_key=True, index=True)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False)
    food_name = Column(String(100), nullable=False)
    is_traditional = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    festival = relationship("Festival")


class UserFestivalPreference(Base):
    """Junction table for user festival preferences"""
    __tablename__ = "user_festival_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    festival_id = Column(Integer, ForeignKey("festivals.id"), nullable=False)
    preference_level = Column(String(20), nullable=False)  # celebrate, observe, ignore
    include_traditional_foods = Column(Boolean, default=True)
    
    # Soft delete (user can disable/enable festival preferences)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="festival_preferences")
    festival = relationship("Festival")
