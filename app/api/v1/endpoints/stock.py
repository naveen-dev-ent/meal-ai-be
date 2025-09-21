from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from datetime import date, datetime, timedelta
from typing import List, Optional

from utils.api_logger import APILogger, log_endpoint, log_user_action, log_security_event

from app.core.database import get_db
from app.core.security import get_current_user
from utils.auth_decorators import log_access_attempt, get_admin_user, require_family_member
from app.models.user import User, Stock, StockMovement, StockAlert
from app.schemas.stock import (
    StockCreate, StockUpdate, StockResponse, StockList, StockSearch,
    StockMovementCreate, StockAlert, StockAnalytics, StockImport, StockExport
)
from app.schemas.stock_categories import (
    StockCategoryResponse, FamilyStockAssignment, StockCategoryAnalytics,
    CategoryStatsResponse, FamilyStockDistribution, StockAssignmentCreate
)
from app.core.cache import cache_manager
from app.services.stock_service import StockService
from app.api.v1.endpoints.stock_categories import router as categories_router

router = APIRouter()
stock_service = StockService()


@router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
@log_endpoint("create_stock_item")
async def create_stock_item(
    stock_data: StockCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new stock item"""
    APILogger.log_request(request, current_user.id)
    
    try:
        # Set user/family ID
        if current_user.family_id:
            stock_data.family_id = current_user.family_id
        else:
            stock_data.user_id = current_user.id
        
        # Create stock item
        stock = Stock(**stock_data.dict())
        db.add(stock)
        db.commit()
        db.refresh(stock)
        
        # Clear cache
        await cache_manager.delete(f"stock:user:{current_user.id}")
        if current_user.family_id:
            await cache_manager.delete(f"stock:family:{current_user.family_id}")
        
        return stock
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("CREATE", "stock", False, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create stock item: {str(e)}"
        )


@router.get("/", response_model=List[StockList])
@log_endpoint("get_stock_items")
async def get_stock_items(
    request: Request,
    search: StockSearch = Depends(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get stock items for current user or family"""
    APILogger.log_request(request, current_user.id)
    
    try:
        # Enhanced search with categorization filters
        query = db.query(Stock)
        
        # Apply user/family filter
        if current_user.family_id:
            query = query.filter(Stock.family_id == current_user.family_id)
        else:
            query = query.filter(Stock.user_id == current_user.id)
        
        # Apply basic search filters
        if search.query:
            query = query.filter(
                or_(
                    Stock.item_name.ilike(f"%{search.query}%"),
                    Stock.brand.ilike(f"%{search.query}%"),
                    Stock.subcategory.ilike(f"%{search.query}%")
                )
            )
        
        if search.category:
            query = query.filter(Stock.category == search.category)
        
        if search.subcategory:
            query = query.filter(Stock.subcategory.ilike(f"%{search.subcategory}%"))
        
        if search.brand:
            query = query.filter(Stock.brand.ilike(f"%{search.brand}%"))
        
        if search.is_perishable is not None:
            query = query.filter(Stock.is_perishable == search.is_perishable)
        
        if search.requires_refrigeration is not None:
            query = query.filter(Stock.requires_refrigeration == search.requires_refrigeration)
        
        # Enhanced categorization filters
        if search.is_special_care is not None:
            query = query.filter(Stock.is_special_care_item == search.is_special_care)
        
        if search.special_care_types:
            # Filter by special care types (JSON array search)
            for care_type in search.special_care_types:
                query = query.filter(Stock.special_care_types.like(f"%{care_type}%"))
        
        if search.is_pet_food is not None:
            query = query.filter(Stock.is_pet_food == search.is_pet_food)
        
        if search.pet_type:
            query = query.filter(Stock.pet_type == search.pet_type)
        
        if search.storage_type:
            query = query.filter(Stock.storage_type == search.storage_type)
        
        if search.priority_level:
            query = query.filter(Stock.priority_level == search.priority_level)
        
        # Health & Diet filters
        if search.is_organic is not None:
            query = query.filter(Stock.is_organic == search.is_organic)
        
        if search.is_gluten_free is not None:
            query = query.filter(Stock.is_gluten_free == search.is_gluten_free)
        
        if search.is_vegan is not None:
            query = query.filter(Stock.is_vegan == search.is_vegan)
        
        if search.is_diabetic_friendly is not None:
            query = query.filter(Stock.is_diabetic_friendly == search.is_diabetic_friendly)
        
        # Family Assignment filters
        if search.assignment_type:
            query = query.filter(Stock.assignment_type == search.assignment_type)
        
        if search.assigned_to_user_id:
            query = query.filter(
                or_(
                    Stock.user_id == search.assigned_to_user_id,
                    Stock.special_care_user_id == search.assigned_to_user_id
                )
            )
        
        # Price and Date filters
        if search.min_price is not None:
            query = query.filter(Stock.price_per_unit >= search.min_price)
        
        if search.max_price is not None:
            query = query.filter(Stock.price_per_unit <= search.max_price)
        
        if search.expiry_before:
            query = query.filter(Stock.expiry_date <= search.expiry_before)
        
        if search.expiry_after:
            query = query.filter(Stock.expiry_date >= search.expiry_after)
        
        if search.low_stock_only:
            query = query.filter(Stock.current_quantity <= Stock.minimum_quantity)
        
        if search.expiring_soon_only:
            expiry_threshold = date.today() + timedelta(days=7)
            query = query.filter(Stock.expiry_date <= expiry_threshold)
        
        # Order by category and name
        stock_items = query.order_by(Stock.category, Stock.item_name).all()
        
        return stock_items
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch stock items: {str(e)}"
        )


@router.get("/{stock_id}", response_model=StockResponse)
async def get_stock_item(
    stock_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific stock item by ID"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock item not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if stock.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if stock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return stock


@router.put("/{stock_id}", response_model=StockResponse)
@log_endpoint("update_stock_item")
async def update_stock_item(
    stock_id: int,
    stock_update: StockUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a stock item"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock item not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if stock.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if stock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        # Update stock fields
        for field, value in stock_update.dict(exclude_unset=True).items():
            setattr(stock, field, value)
        
        stock.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(stock)
        
        # Clear cache
        await cache_manager.delete(f"stock:user:{current_user.id}")
        if current_user.family_id:
            await cache_manager.delete(f"stock:family:{current_user.family_id}")
        
        return stock
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("UPDATE", "stock", False, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update stock item: {str(e)}"
        )


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
@log_endpoint("delete_stock_item")
async def delete_stock_item(
    stock_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a stock item"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock item not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if stock.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if stock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        db.delete(stock)
        db.commit()
        
        # Clear cache
        await cache_manager.delete(f"stock:user:{current_user.id}")
        if current_user.family_id:
            await cache_manager.delete(f"stock:family:{current_user.family_id}")
        
        APILogger.log_database_operation("DELETE", "stock", True, current_user.id)
        log_user_action("Stock Item Deleted", current_user.id, f"Item ID: {stock_id}")
        
        return None
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("DELETE", "stock", False, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete stock item: {str(e)}"
        )


@router.post("/{stock_id}/movement", response_model=StockMovementCreate, status_code=status.HTTP_201_CREATED)
async def record_stock_movement(
    stock_id: int,
    movement_data: StockMovementCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a stock movement (addition, consumption, etc.)"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock item not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if stock.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if stock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        # Update stock quantity
        stock.current_quantity += movement_data.quantity_change
        
        if stock.current_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock quantity cannot be negative"
            )
        
        # Create movement record
        movement = StockMovement(
            stock_id=stock_id,
            **movement_data.dict()
        )
        
        db.add(movement)
        stock.updated_at = datetime.utcnow()
        db.commit()
        
        # Clear cache
        await cache_manager.delete(f"stock:user:{current_user.id}")
        if current_user.family_id:
            await cache_manager.delete(f"stock:family:{current_user.family_id}")
        
        return movement
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to record stock movement: {str(e)}"
        )


@router.get("/{stock_id}/movements", response_model=List[StockMovementCreate])
async def get_stock_movements(
    stock_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get movement history for a stock item"""
    # Check if stock exists and user has access
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock item not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if stock.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if stock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Build query
    query = db.query(StockMovement).filter(StockMovement.stock_id == stock_id)
    
    if start_date:
        query = query.filter(StockMovement.date >= start_date)
    if end_date:
        query = query.filter(StockMovement.date <= end_date)
    
    movements = query.order_by(StockMovement.date.desc()).all()
    return movements


@router.post("/{stock_id}/alert", response_model=StockAlert, status_code=status.HTTP_201_CREATED)
async def create_stock_alert(
    stock_id: int,
    alert_data: StockAlert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a stock alert"""
    # Check if stock exists and user has access
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock item not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if stock.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if stock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        # Create alert
        alert = StockAlert(
            stock_id=stock_id,
            **alert_data.dict()
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        return alert
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create stock alert: {str(e)}"
        )


@router.get("/alerts", response_model=List[StockAlert])
async def get_stock_alerts(
    is_resolved: Optional[bool] = Query(None),
    priority: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get stock alerts for current user or family"""
    try:
        # Get stock IDs for user/family
        stock_query = db.query(Stock.id)
        
        if current_user.family_id:
            stock_query = stock_query.filter(Stock.family_id == current_user.family_id)
        else:
            stock_query = stock_query.filter(Stock.user_id == current_user.id)
        
        stock_ids = [stock.id for stock in stock_query.all()]
        
        if not stock_ids:
            return []
        
        # Get alerts
        query = db.query(StockAlert).filter(StockAlert.stock_id.in_(stock_ids))
        
        if is_resolved is not None:
            query = query.filter(StockAlert.is_resolved == is_resolved)
        if priority:
            query = query.filter(StockAlert.priority == priority)
        
        alerts = query.order_by(StockAlert.priority.desc(), StockAlert.created_at.desc()).all()
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch stock alerts: {str(e)}"
        )


@router.put("/alerts/{alert_id}/resolve", response_model=StockAlert)
async def resolve_stock_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resolve a stock alert"""
    alert = db.query(StockAlert).filter(StockAlert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock alert not found"
        )
    
    # Check access permissions through stock
    stock = db.query(Stock).filter(Stock.id == alert.stock_id).first()
    
    if current_user.family_id:
        if stock.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if stock.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = current_user.id
        db.commit()
        db.refresh(alert)
        
        return alert
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to resolve alert: {str(e)}"
        )


# Stock Analytics with Enhanced Categorization
@router.get("/analytics", response_model=StockAnalytics)
@require_family_member
@log_access_attempt("stock_analytics")
async def get_stock_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive stock analytics including:
    - Total items and value
    - Low stock alerts
    - Expiring items
    - Enhanced category distribution
    - Pet food and special care analytics
    - Storage and priority distribution
    - Health and diet analytics
    - Family assignment analytics
    - Consumption trends
    """
    try:
        APILogger.log_request("GET", "/stock/analytics", current_user.id)
        
        stock_service = StockService()
        analytics = await stock_service.get_stock_analytics(
            user_id=current_user.id,
            family_id=current_user.family_id,
            db=db
        )
        
        APILogger.log_user_action(current_user.id, "view_stock_analytics", "Enhanced stock analytics viewed")
        return analytics
        
    except Exception as e:
        APILogger.log_error(f"Stock analytics failed: {str(e)}", current_user.id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import/csv", status_code=status.HTTP_201_CREATED)
@log_access_attempt("stock_import")
async def import_stock_csv(
    file: UploadFile = File(...),
    overwrite_existing: bool = Query(False),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Import stock items from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    try:
        # Read CSV content
        content = await file.read()
        csv_text = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        imported_count = 0
        errors = []
        
        for row in csv_reader:
            try:
                # Create stock item
                stock_data = StockCreate(
                    item_name=row['item_name'],
                    category=row['category'],
                    weight=float(row['weight']),
                    unit=row.get('unit', 'kg'),
                    current_quantity=float(row['current_quantity']),
                    minimum_quantity=float(row.get('minimum_quantity', 0)),
                    price_per_unit=float(row.get('price_per_unit', 0)) if row.get('price_per_unit') else None,
                    is_perishable=row.get('is_perishable', 'false').lower() == 'true',
                    requires_refrigeration=row.get('requires_refrigeration', 'false').lower() == 'true'
                )
                
                # Set user/family ID
                if current_user.family_id:
                    stock_data.family_id = current_user.family_id
                else:
                    stock_data.user_id = current_user.id
                
                # Check if item exists
                existing_item = db.query(Stock).filter(
                    Stock.item_name == stock_data.item_name,
                    Stock.family_id == stock_data.family_id,
                    Stock.user_id == stock_data.user_id
                ).first()
                
                if existing_item and overwrite_existing:
                    # Update existing item
                    for field, value in stock_data.dict(exclude_unset=True).items():
                        setattr(existing_item, field, value)
                    existing_item.updated_at = datetime.utcnow()
                elif not existing_item:
                    # Create new item
                    stock = Stock(**stock_data.dict())
                    db.add(stock)
                
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {imported_count + 1}: {str(e)}")
        
        db.commit()
        
        # Clear cache
        await cache_manager.delete(f"stock:user:{current_user.id}")
        if current_user.family_id:
            await cache_manager.delete(f"stock:family:{current_user.family_id}")
        
        return {
            "message": f"Successfully imported {imported_count} stock items",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import CSV: {str(e)}"
        )


@router.get("/export/csv")
async def export_stock_csv(
    include_nutritional_info: bool = Query(True),
    include_pricing: bool = Query(True),
    include_timestamps: bool = Query(False),
    categories: Optional[List[str]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export stock items to CSV"""
    try:
        # Get stock items
        query = db.query(Stock)
        
        if current_user.family_id:
            query = query.filter(Stock.family_id == current_user.family_id)
        else:
            query = query.filter(Stock.user_id == current_user.id)
        
        if categories:
            query = query.filter(Stock.category.in_(categories))
        
        stock_items = query.all()
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        headers = ['item_name', 'category', 'current_quantity', 'unit', 'minimum_quantity']
        
        if include_nutritional_info:
            headers.extend(['calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g'])
        
        if include_pricing:
            headers.extend(['price_per_unit', 'currency'])
        
        headers.extend(['is_perishable', 'requires_refrigeration', 'expiry_date'])
        
        if include_timestamps:
            headers.extend(['created_at', 'updated_at'])
        
        writer.writerow(headers)
        
        # Write data
        for item in stock_items:
            row = [
                item.item_name,
                item.category,
                item.current_quantity,
                item.unit,
                item.minimum_quantity
            ]
            
            if include_nutritional_info:
                row.extend([
                    item.calories_per_100g or '',
                    item.protein_per_100g or '',
                    item.carbs_per_100g or '',
                    item.fat_per_100g or ''
                ])
            
            if include_pricing:
                row.extend([
                    item.price_per_unit or '',
                    item.currency or ''
                ])
            
            row.extend([
                str(item.is_perishable),
                str(item.requires_refrigeration),
                item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else ''
            ])
            
            if include_timestamps:
                row.extend([
                    item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '',
                    item.updated_at.strftime('%Y-%m-%d %H:%M:%S') if item.updated_at else ''
                ])
            
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return {
            "csv_content": csv_content,
            "filename": f"stock_export_{date.today().strftime('%Y%m%d')}.csv"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to export CSV: {str(e)}"
        )
