"""
Enhanced stock categorization API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from utils.auth_decorators import log_access_attempt, get_family_member
from utils.api_logger import APILogger, log_endpoint, log_user_action

from app.models.user import User, Stock, Family
from app.schemas.stock_categories import (
    StockCategoryEnum,
    SpecialCareTypeEnum,
    StorageTypeEnum,
    StockPriorityEnum,
    EnhancedStockCreate,
    StockCategoryStats,
    FamilyStockDistribution,
    StockCategoryAnalytics,
    FamilyMemberStockAssignment
)

router = APIRouter()

@router.get("/categories", response_model=List[str])
@log_endpoint("get_stock_categories")
async def get_stock_categories(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get all available stock categories"""
    APILogger.log_request(request, current_user.id)
    
    return [category.value for category in StockCategoryEnum]

@router.get("/categories/food", response_model=List[str])
@log_endpoint("get_food_categories")
async def get_food_categories(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get food-specific categories"""
    APILogger.log_request(request, current_user.id)
    
    food_categories = [
        StockCategoryEnum.GRAINS_CEREALS,
        StockCategoryEnum.VEGETABLES,
        StockCategoryEnum.FRUITS,
        StockCategoryEnum.DAIRY,
        StockCategoryEnum.MEAT_POULTRY,
        StockCategoryEnum.SEAFOOD,
        StockCategoryEnum.LEGUMES,
        StockCategoryEnum.NUTS_SEEDS,
        StockCategoryEnum.SPICES_HERBS,
        StockCategoryEnum.OILS_FATS,
        StockCategoryEnum.BEVERAGES,
        StockCategoryEnum.SNACKS,
        StockCategoryEnum.CONDIMENTS,
        StockCategoryEnum.BAKING_INGREDIENTS
    ]
    
    return [category.value for category in food_categories]

@router.get("/categories/pet", response_model=List[str])
@log_endpoint("get_pet_categories")
async def get_pet_categories(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get pet food categories"""
    APILogger.log_request(request, current_user.id)
    
    pet_categories = [
        StockCategoryEnum.DOG_FOOD,
        StockCategoryEnum.CAT_FOOD,
        StockCategoryEnum.BIRD_FOOD,
        StockCategoryEnum.FISH_FOOD,
        StockCategoryEnum.PET_TREATS,
        StockCategoryEnum.PET_SUPPLEMENTS
    ]
    
    return [category.value for category in pet_categories]

@router.get("/categories/special-care", response_model=List[str])
@log_endpoint("get_special_care_categories")
async def get_special_care_categories(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get special care food categories"""
    APILogger.log_request(request, current_user.id)
    
    special_categories = [
        StockCategoryEnum.BABY_FOOD,
        StockCategoryEnum.SENIOR_FOOD,
        StockCategoryEnum.DIABETIC_FOOD,
        StockCategoryEnum.GLUTEN_FREE,
        StockCategoryEnum.ORGANIC
    ]
    
    return [category.value for category in special_categories]

@router.get("/family-members/assignments", response_model=List[FamilyStockDistribution])
@log_endpoint("get_family_stock_assignments")
async def get_family_stock_assignments(
    request: Request,
    current_user: User = Depends(get_family_member),
    db: Session = Depends(get_db)
):
    """Get stock assignments for family members"""
    APILogger.log_request(request, current_user.id)
    
    try:
        if not current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not part of a family"
            )
        
        # Get family members
        family = db.query(Family).filter(Family.id == current_user.family_id).first()
        if not family:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family not found"
            )
        
        family_members = family.members
        distributions = []
        
        for member in family_members:
            # Get stock items assigned to this member
            assigned_stocks = db.query(Stock).filter(
                Stock.family_id == current_user.family_id,
                Stock.special_care_user_id == member.id
            ).all()
            
            # Calculate statistics
            total_value = sum(
                (stock.price_per_unit or 0) * stock.current_quantity 
                for stock in assigned_stocks
            )
            
            # Category distribution
            categories = {}
            for stock in assigned_stocks:
                categories[stock.category] = categories.get(stock.category, 0) + 1
            
            distributions.append(FamilyStockDistribution(
                family_member_id=member.id,
                family_member_name=f"{member.first_name} {member.last_name}",
                assigned_items=len(assigned_stocks),
                exclusive_items=len([s for s in assigned_stocks if s.is_special_care_item]),
                total_value=total_value,
                categories=categories
            ))
        
        return distributions
        
    except Exception as e:
        APILogger.log_error(f"Failed to get family stock assignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get family stock assignments: {str(e)}"
        )

@router.post("/family-members/{member_id}/assign", status_code=status.HTTP_201_CREATED)
@log_endpoint("assign_stock_to_member")
@log_access_attempt("stock_assignment")
async def assign_stock_to_family_member(
    member_id: int,
    stock_id: int,
    assignment_type: str = "shared",
    notes: Optional[str] = None,
    request: Request = None,
    current_user: User = Depends(get_family_member),
    db: Session = Depends(get_db)
):
    """Assign stock item to specific family member"""
    APILogger.log_request(request, current_user.id)
    
    try:
        # Verify family membership
        if not current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not part of a family"
            )
        
        # Get stock item
        stock = db.query(Stock).filter(
            Stock.id == stock_id,
            Stock.family_id == current_user.family_id
        ).first()
        
        if not stock:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stock item not found"
            )
        
        # Verify family member exists
        family_member = db.query(User).filter(
            User.id == member_id,
            User.family_id == current_user.family_id
        ).first()
        
        if not family_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family member not found"
            )
        
        # Update stock assignment
        stock.special_care_user_id = member_id
        if assignment_type == "exclusive":
            stock.is_special_care_item = True
        
        db.commit()
        
        # Log the assignment
        log_user_action(
            "Stock Assignment",
            current_user.id,
            f"Assigned stock '{stock.item_name}' to {family_member.first_name} {family_member.last_name}",
            {
                "stock_id": stock_id,
                "assigned_to": member_id,
                "assignment_type": assignment_type,
                "notes": notes
            }
        )
        
        return {
            "message": f"Stock item assigned to {family_member.first_name} {family_member.last_name}",
            "assignment_type": assignment_type
        }
        
    except Exception as e:
        db.rollback()
        APILogger.log_error(f"Failed to assign stock to family member: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign stock: {str(e)}"
        )

@router.get("/analytics/categories", response_model=StockCategoryAnalytics)
@log_endpoint("get_category_analytics")
async def get_stock_category_analytics(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive stock analytics by categories"""
    APILogger.log_request(request, current_user.id)
    
    try:
        # Get stock items
        query = db.query(Stock)
        if current_user.family_id:
            query = query.filter(Stock.family_id == current_user.family_id)
        else:
            query = query.filter(Stock.user_id == current_user.id)
        
        stock_items = query.all()
        
        # Category statistics
        category_stats = {}
        for item in stock_items:
            category = item.category
            if category not in category_stats:
                category_stats[category] = {
                    "total_items": 0,
                    "total_value": 0,
                    "low_stock_items": 0,
                    "expiring_soon_items": 0,
                    "items": []
                }
            
            stats = category_stats[category]
            stats["total_items"] += 1
            stats["total_value"] += (item.price_per_unit or 0) * item.current_quantity
            stats["items"].append(item.item_name)
            
            # Check low stock
            if item.current_quantity <= item.minimum_quantity:
                stats["low_stock_items"] += 1
            
            # Check expiring soon
            if item.expiry_date and item.expiry_date <= datetime.now() + timedelta(days=7):
                stats["expiring_soon_items"] += 1
        
        # Convert to response format
        category_stats_list = []
        for category, stats in category_stats.items():
            category_stats_list.append(StockCategoryStats(
                category=category,
                total_items=stats["total_items"],
                total_value=stats["total_value"],
                low_stock_items=stats["low_stock_items"],
                expiring_soon_items=stats["expiring_soon_items"],
                top_items=stats["items"][:5]  # Top 5 items
            ))
        
        # Family distribution (if applicable)
        family_distribution = []
        if current_user.family_id:
            family_distribution = await get_family_stock_assignments(request, current_user, db)
        
        # Pet food statistics
        pet_items = [item for item in stock_items if item.is_pet_food]
        pet_food_stats = {
            "total_pet_items": len(pet_items),
            "total_pet_value": sum((item.price_per_unit or 0) * item.current_quantity for item in pet_items),
            "pet_categories": list(set(item.category for item in pet_items))
        }
        
        # Special care statistics
        special_care_items = [item for item in stock_items if item.is_special_care_item]
        special_care_stats = {
            "total_special_care_items": len(special_care_items),
            "total_special_care_value": sum((item.price_per_unit or 0) * item.current_quantity for item in special_care_items),
            "assigned_members": len(set(item.special_care_user_id for item in special_care_items if item.special_care_user_id))
        }
        
        # Storage distribution
        storage_distribution = {}
        for item in stock_items:
            if item.requires_refrigeration:
                storage_type = "refrigerator"
            else:
                storage_type = "pantry"
            storage_distribution[storage_type] = storage_distribution.get(storage_type, 0) + 1
        
        # Priority distribution (placeholder - would need to add priority field to model)
        priority_distribution = {
            "essential": len([item for item in stock_items if item.current_quantity <= item.minimum_quantity]),
            "important": len([item for item in stock_items if item.is_special_care_item]),
            "nice_to_have": len(stock_items) - len([item for item in stock_items if item.current_quantity <= item.minimum_quantity or item.is_special_care_item])
        }
        
        return StockCategoryAnalytics(
            total_categories=len(category_stats),
            category_stats=category_stats_list,
            family_distribution=family_distribution,
            pet_food_stats=pet_food_stats,
            special_care_stats=special_care_stats,
            storage_distribution=storage_distribution,
            priority_distribution=priority_distribution
        )
        
    except Exception as e:
        APILogger.log_error(f"Failed to get category analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get category analytics: {str(e)}"
        )

@router.get("/special-care/types", response_model=List[str])
@log_endpoint("get_special_care_types")
async def get_special_care_types(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get available special care types"""
    APILogger.log_request(request, current_user.id)
    
    return [care_type.value for care_type in SpecialCareTypeEnum]

@router.get("/storage/types", response_model=List[str])
@log_endpoint("get_storage_types")
async def get_storage_types(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get available storage types"""
    APILogger.log_request(request, current_user.id)
    
    return [storage_type.value for storage_type in StorageTypeEnum]
