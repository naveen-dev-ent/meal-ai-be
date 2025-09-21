from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
import json

from utils.api_logger import APILogger, log_endpoint, log_user_action, log_security_event

from app.core.database import get_db
from app.core.security import get_current_user
from utils.auth_decorators import get_chef_user, log_access_attempt, require_family_access
from app.models.user import User, Meal, MealFeedback, Family
from app.schemas.meals import (
    MealCreate,
    MealUpdate,
    MealResponse,
    MealList,
    MealApproval,
    MealGenerationRequest,
    MealGenerationResponse,
    MealFeedbackCreate,
    MealFeedbackUpdate,
    MealFeedbackResponse,
    MealPlan,
    MealHistory,
    MealAnalytics
)
from app.core.factory import get_service_factory
from app.services.meal_service import MealService

router = APIRouter()
service_factory = get_service_factory()
meal_service = service_factory.get_service("meal")


@router.post("/", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
@log_endpoint("create_meal")
async def create_meal(
    meal_data: MealCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new meal"""
    APILogger.log_request(request, current_user.id)
    
    try:
        # Set user/family ID
        if current_user.family_id:
            meal_data.family_id = current_user.family_id
        else:
            meal_data.user_id = current_user.id
        
        # Create meal
        meal = Meal(**meal_data.dict())
        db.add(meal)
        db.commit()
        db.refresh(meal)
        
        # Clear cache
        await meal_service.cache_service.delete(f"meals:user:{current_user.id}")
        if current_user.family_id:
            await meal_service.cache_service.delete(f"meals:family:{current_user.family_id}")
        
        return meal
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("CREATE", "meals", False, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create meal: {str(e)}"
        )


@router.get("/", response_model=List[MealList])
@log_endpoint("get_meals")
async def get_meals(
    request: Request,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    meal_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get meals for current user or family"""
    APILogger.log_request(request, current_user.id)
    
    try:
        # Build query
        query = db.query(Meal)
        
        if current_user.family_id:
            query = query.filter(Meal.family_id == current_user.family_id)
        else:
            query = query.filter(Meal.user_id == current_user.id)
        
        # Apply filters
        if start_date:
            query = query.filter(Meal.planned_date >= start_date)
        if end_date:
            query = query.filter(Meal.planned_date <= end_date)
        if meal_type:
            query = query.filter(Meal.meal_type == meal_type)
        if status:
            query = query.filter(Meal.status == status)
        
        # Order by date and time
        meals = query.order_by(Meal.planned_date, Meal.planned_time).all()
        
        return meals
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch meals: {str(e)}"
        )


@router.get("/{meal_id}", response_model=MealResponse)
@log_endpoint("get_meal")
async def get_meal(
    meal_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific meal by ID"""
    APILogger.log_request(request, current_user.id)
    
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if meal.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if meal.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return meal


@router.put("/{meal_id}", response_model=MealResponse)
@log_endpoint("update_meal")
async def update_meal(
    meal_id: int,
    meal_update: MealUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a meal"""
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if meal.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if meal.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        # Update meal fields
        for field, value in meal_update.dict(exclude_unset=True).items():
            setattr(meal, field, value)
        
        meal.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(meal)
        
        # Clear cache
        await meal_service.cache_service.delete(f"meals:user:{current_user.id}")
        if current_user.family_id:
            await meal_service.cache_service.delete(f"meals:family:{current_user.family_id}")
        
        return meal
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("UPDATE", "meals", False, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update meal: {str(e)}"
        )


@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
@log_endpoint("delete_meal")
async def delete_meal(
    meal_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a meal"""
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if meal.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if meal.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        db.delete(meal)
        db.commit()
        
        # Clear cache
        await meal_service.cache_service.delete(f"meals:user:{current_user.id}")
        if current_user.family_id:
            await meal_service.cache_service.delete(f"meals:family:{current_user.family_id}")
        
        APILogger.log_database_operation("DELETE", "meals", True, current_user.id)
        log_user_action("Meal Deleted", current_user.id, f"Meal ID: {meal_id}")
        
        return None
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("DELETE", "meals", False, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete meal: {str(e)}"
        )


@router.post("/{meal_id}/approve", response_model=MealResponse)
@log_access_attempt("meal_approval")
async def approve_meal(
    meal_id: int,
    approval: MealApproval,
    request: Request,
    current_user: User = Depends(get_chef_user),
    db: Session = Depends(get_db)
):
    """Approve or reject a meal (for decision makers)"""
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Check if user is decision maker
    if current_user.family_id:
        if not current_user.is_decision_maker:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only decision makers can approve meals"
            )
        if meal.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if meal.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        meal.is_approved = approval.is_approved
        meal.approved_by = current_user.id
        meal.status = "approved" if approval.is_approved else "planned"
        meal.updated_at = datetime.utcnow()
        
        if approval.notes:
            meal.feedback = approval.notes
        
        db.commit()
        db.refresh(meal)
        
        return meal
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to approve meal: {str(e)}"
        )


@router.post("/generate", response_model=MealGenerationResponse)
@log_endpoint("generate_meals")
@log_access_attempt("meal_generation")
async def generate_meals(
    generation_request: MealGenerationRequest,
    request: Request,
    current_user: User = Depends(get_chef_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered meal suggestions"""
    APILogger.log_request(request, current_user.id)
    
    try:
        # Set user/family ID
        if current_user.family_id:
            generation_request.family_id = current_user.family_id
        else:
            generation_request.user_id = current_user.id
        
        # Generate meals using service
        generated_meals = await meal_service.generate_meals(generation_request, db)
        
        log_user_action("AI Meals Generated", current_user.id, f"Generated {len(generated_meals.meals) if hasattr(generated_meals, 'meals') else 'N/A'} meals")
        
        return generated_meals
    except Exception as e:
        APILogger.log_error("generate_meals", e, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate meals: {str(e)}"
        )


@router.post("/{meal_id}/feedback", response_model=MealFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def add_meal_feedback(
    meal_id: int,
    feedback_data: MealFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add feedback to a meal"""
    # Check if meal exists and user has access
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if meal.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if meal.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    try:
        # Create feedback
        feedback = MealFeedback(
            meal_id=meal_id,
            user_id=current_user.id,
            **feedback_data.dict()
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        # Update meal rating if provided
        if feedback_data.rating:
            meal.rating = feedback_data.rating
            db.commit()
        
        return feedback
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add feedback: {str(e)}"
        )


@router.get("/{meal_id}/feedback", response_model=List[MealFeedbackResponse])
async def get_meal_feedback(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all feedback for a meal"""
    # Check if meal exists and user has access
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    
    if not meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found"
        )
    
    # Check access permissions
    if current_user.family_id:
        if meal.family_id != current_user.family_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if meal.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    feedback = db.query(MealFeedback).filter(MealFeedback.meal_id == meal_id).all()
    return feedback


@router.get("/plan/daily", response_model=MealPlan)
async def get_daily_meal_plan(
    date: date = Query(default_factory=date.today),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily meal plan"""
    try:
        # Get meals for the specified date
        query = db.query(Meal)
        
        if current_user.family_id:
            query = query.filter(Meal.family_id == current_user.family_id)
        else:
            query = query.filter(Meal.user_id == current_user.id)
        
        meals = query.filter(Meal.planned_date == date).order_by(Meal.planned_time).all()
        
        # Calculate totals
        total_nutrition = {
            "calories": sum(m.total_calories or 0 for m in meals),
            "protein": sum(m.total_protein or 0 for m in meals),
            "carbs": sum(m.total_carbs or 0 for m in meals),
            "fat": sum(m.total_fat or 0 for m in meals)
        }
        
        # Generate shopping list
        shopping_list = []
        for meal in meals:
            if meal.ingredients:
                try:
                    ingredients = json.loads(meal.ingredients)
                    for ingredient in ingredients:
                        shopping_list.append(f"{ingredient['name']} - {ingredient['quantity']} {ingredient['unit']}")
                except:
                    pass
        
        # Remove duplicates
        shopping_list = list(set(shopping_list))
        
        # Estimate cost (placeholder)
        estimated_cost = len(meals) * 5.0  # $5 per meal average
        
        return MealPlan(
            date=date,
            meals=meals,
            total_nutrition=total_nutrition,
            shopping_list=shopping_list,
            estimated_cost=estimated_cost
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get meal plan: {str(e)}"
        )


@router.get("/history", response_model=List[MealHistory])
async def get_meal_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get meal history with analytics"""
    try:
        # Set default date range if not provided
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get meals in date range
        query = db.query(Meal)
        
        if current_user.family_id:
            query = query.filter(Meal.family_id == current_user.family_id)
        else:
            query = query.filter(Meal.user_id == current_user.id)
        
        meals = query.filter(
            Meal.planned_date >= start_date,
            Meal.planned_date <= end_date
        ).order_by(Meal.planned_date.desc()).all()
        
        # Group by date
        meals_by_date = {}
        for meal in meals:
            if meal.planned_date not in meals_by_date:
                meals_by_date[meal.planned_date] = []
            meals_by_date[meal.planned_date].append(meal)
        
        # Create history entries
        history = []
        for date, day_meals in meals_by_date.items():
            total_calories = sum(m.total_calories or 0 for m in day_meals)
            ratings = [m.rating for m in day_meals if m.rating]
            average_rating = sum(ratings) / len(ratings) if ratings else None
            
            history.append(MealHistory(
                date=date,
                meals=day_meals,
                total_calories=total_calories,
                average_rating=average_rating,
                feedback_count=len([m for m in day_meals if m.feedback])
            ))
        
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get meal history: {str(e)}"
        )


@router.get("/analytics", response_model=MealAnalytics)
async def get_meal_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive meal analytics"""
    try:
        # Set default date range if not provided
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get meals in date range
        query = db.query(Meal)
        
        if current_user.family_id:
            query = query.filter(Meal.family_id == current_user.family_id)
        else:
            query = query.filter(Meal.user_id == current_user.id)
        
        meals = query.filter(
            Meal.planned_date >= start_date,
            Meal.planned_date <= end_date
        ).all()
        
        # Calculate analytics
        total_meals = len(meals)
        ratings = [m.rating for m in meals if m.rating]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Get favorite and least favorite meals
        meal_ratings = {}
        for meal in meals:
            if meal.rating:
                if meal.name not in meal_ratings:
                    meal_ratings[meal.name] = []
                meal_ratings[meal.name].append(meal.rating)
        
        favorite_meals = []
        least_favorite_meals = []
        
        for meal_name, ratings_list in meal_ratings.items():
            avg = sum(ratings_list) / len(ratings_list)
            if avg >= 4:
                favorite_meals.append(meal_name)
            elif avg <= 2:
                least_favorite_meals.append(meal_name)
        
        # Nutritional totals
        nutritional_totals = {
            "calories": sum(m.total_calories or 0 for m in meals),
            "protein": sum(m.total_protein or 0 for m in meals),
            "carbs": sum(m.total_carbs or 0 for m in meals),
            "fat": sum(m.total_fat or 0 for m in meals)
        }
        
        # Cost analysis (placeholder)
        cost_analysis = {
            "total_cost": total_meals * 5.0,  # $5 per meal average
            "average_cost_per_meal": 5.0,
            "cost_trend": "stable"
        }
        
        # Meal type distribution
        meal_type_distribution = {}
        for meal in meals:
            meal_type_distribution[meal.meal_type] = meal_type_distribution.get(meal.meal_type, 0) + 1
        
        return MealAnalytics(
            total_meals=total_meals,
            average_rating=average_rating,
            favorite_meals=favorite_meals,
            least_favorite_meals=least_favorite_meals,
            nutritional_totals=nutritional_totals,
            cost_analysis=cost_analysis,
            meal_type_distribution=meal_type_distribution
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get meal analytics: {str(e)}"
        )
