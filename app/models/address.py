from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Address(Base):
    """Normalized address table following 3NF"""
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    street_address = Column(Text, nullable=False)
    postal_code = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False)
    state_province = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False)
    
    # Address type and ownership
    address_type = Column(String(20), nullable=False)  # current, native, office, etc.
    is_primary = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


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
