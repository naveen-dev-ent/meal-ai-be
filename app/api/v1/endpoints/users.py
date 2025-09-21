from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.core.security import get_current_user
from utils.auth_decorators import get_family_decision_maker, log_access_attempt, require_self_or_admin
from app.models.user import User, Family
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    UserList,
    UserProfile
)
from app.core.cache import cache_manager
from utils.api_logger import APILogger, log_endpoint

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
@log_endpoint("get_user_profile")
async def get_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    APILogger.log_request(request, current_user.id)
    APILogger.log_user_action(current_user.id, "profile_view", "Viewed user profile")
    return current_user


@router.put("/profile", response_model=UserProfile)
@log_endpoint("update_user_profile")
async def update_user_profile(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    APILogger.log_request(request, current_user.id)
    try:
        # Update user fields
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        APILogger.log_database_operation("UPDATE", "user_profile", True, current_user.id)
        APILogger.log_user_action(current_user.id, "profile_update", f"Updated profile fields: {list(user_update.dict(exclude_unset=True).keys())}")
        
        # Clear cache
        await cache_manager.delete(f"user:{current_user.id}")
        
        return current_user
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("UPDATE", "user_profile", False, current_user.id)
        APILogger.log_error(f"Profile update failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/profile/full", response_model=UserResponse)
@log_endpoint("get_full_user_profile")
async def get_full_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's full profile with all details"""
    APILogger.log_request(request, current_user.id)
    APILogger.log_user_action(current_user.id, "full_profile_view", "Viewed full user profile")
    return current_user


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
@log_endpoint("delete_user_profile")
async def delete_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's profile (soft delete)"""
    client_ip = request.client.host if request.client else "Unknown"
    APILogger.log_request(request, current_user.id)
    APILogger.log_security_event(f"User profile deletion requested by user {current_user.id} from IP {client_ip}")
    try:
        # Soft delete - mark as inactive
        current_user.is_active = False
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        APILogger.log_database_operation("DELETE", "user_profile", True, current_user.id)
        APILogger.log_user_action(current_user.id, "profile_delete", "User profile soft deleted")
        
        # Clear cache
        await cache_manager.delete(f"user:{current_user.id}")
        await cache_manager.delete(f"session:user:{current_user.id}")
        
        return None
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("DELETE", "user_profile", False, current_user.id)
        APILogger.log_error(f"Profile deletion failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete profile: {str(e)}"
        )


@router.get("/family/members", response_model=List[UserList])
@log_endpoint("get_family_members")
async def get_family_members(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of the current user's family"""
    APILogger.log_request(request, current_user.id)
    if not current_user.family_id:
        APILogger.log_error(f"User {current_user.id} attempted to get family members without being in a family")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of a family"
        )
    
    try:
        family_members = db.query(User).filter(
            User.family_id == current_user.family_id,
            User.is_active == True
        ).all()
        
        APILogger.log_user_action(current_user.id, "family_members_view", f"Viewed {len(family_members)} family members")
        return family_members
    except Exception as e:
        APILogger.log_error(f"Failed to get family members for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get family members: {str(e)}"
        )


@router.post("/family/invite", status_code=status.HTTP_201_CREATED)
@log_endpoint("invite_family_member")
@log_access_attempt("family_invite")
async def invite_family_member(
    email: str,
    request: Request,
    current_user: User = Depends(get_family_decision_maker),
    db: Session = Depends(get_db)
):
    """Invite a user to join the family"""
    client_ip = request.client.host if request.client else "Unknown"
    APILogger.log_request(request, current_user.id)
    APILogger.log_security_event(f"Family invitation attempt by user {current_user.id} for email {email} from IP {client_ip}")
    
    if not current_user.is_decision_maker:
        APILogger.log_security_event(f"Unauthorized family invite attempt by non-decision-maker user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only decision makers can invite family members"
        )
    
    if not current_user.family_id:
        APILogger.log_error(f"User {current_user.id} attempted family invite without being in a family")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of a family"
        )
    
    try:
        # Check if user exists
        invited_user = db.query(User).filter(User.email == email).first()
        if not invited_user:
            APILogger.log_error(f"Family invite failed - user not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if invited_user.family_id:
            APILogger.log_error(f"Family invite failed - user {email} already in family")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already part of a family"
            )
        
        # Add user to family
        invited_user.family_id = current_user.family_id
        invited_user.is_family_account = True
        invited_user.updated_at = datetime.utcnow()
        
        db.commit()
        
        APILogger.log_database_operation("UPDATE", "family_invite", True, current_user.id)
        APILogger.log_user_action(current_user.id, "family_invite", f"Invited user {email} to family")
        
        # TODO: Send invitation email/notification
        
        return {"message": f"Successfully invited {email} to the family"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("UPDATE", "family_invite", False, current_user.id)
        APILogger.log_error(f"Family invitation failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to invite family member: {str(e)}"
        )


@router.delete("/family/remove/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@log_endpoint("remove_family_member")
@log_access_attempt("family_remove")
async def remove_family_member(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_family_decision_maker),
    db: Session = Depends(get_db)
):
    """Remove a member from the family"""
    client_ip = request.client.host if request.client else "Unknown"
    APILogger.log_request(request, current_user.id)
    APILogger.log_security_event(f"Family member removal attempt by user {current_user.id} for user_id {user_id} from IP {client_ip}")
    
    if not current_user.is_decision_maker:
        APILogger.log_security_event(f"Unauthorized family removal attempt by non-decision-maker user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only decision makers can remove family members"
        )
    
    if not current_user.family_id:
        APILogger.log_error(f"User {current_user.id} attempted family removal without being in a family")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of a family"
        )
    
    try:
        # Check if user is in the same family
        member_to_remove = db.query(User).filter(
            User.id == user_id,
            User.family_id == current_user.family_id
        ).first()
        
        if not member_to_remove:
            APILogger.log_error(f"Family removal failed - member not found: user_id {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family member not found"
            )
        
        if member_to_remove.id == current_user.id:
            APILogger.log_error(f"User {current_user.id} attempted to remove themselves from family")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself from family"
            )
        
        # Remove from family
        member_to_remove.family_id = None
        member_to_remove.is_family_account = False
        member_to_remove.is_decision_maker = False
        member_to_remove.is_chef = False
        member_to_remove.updated_at = datetime.utcnow()
        
        db.commit()
        
        APILogger.log_database_operation("UPDATE", "family_removal", True, current_user.id)
        APILogger.log_user_action(current_user.id, "family_remove", f"Removed user {user_id} from family")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("UPDATE", "family_removal", False, current_user.id)
        APILogger.log_error(f"Family removal failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove family member: {str(e)}"
        )


@router.put("/family/role/{user_id}", response_model=UserResponse)
@log_endpoint("update_family_role")
async def update_family_role(
    user_id: int,
    request: Request,
    is_decision_maker: Optional[bool] = None,
    is_chef: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update family member roles"""
    APILogger.log_request(request, current_user.id)
    if not current_user.is_decision_maker:
        APILogger.log_security_event(f"Unauthorized role update attempt by non-decision-maker user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only decision makers can update family roles"
        )
    
    if not current_user.family_id:
        APILogger.log_error(f"User {current_user.id} attempted role update without being in a family")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of a family"
        )
    
    try:
        # Check if user is in the same family
        member = db.query(User).filter(
            User.id == user_id,
            User.family_id == current_user.family_id
        ).first()
        
        if not member:
            APILogger.log_error(f"Role update failed - member not found: user_id {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Family member not found"
            )
        
        # Update roles
        role_changes = []
        if is_decision_maker is not None:
            member.is_decision_maker = is_decision_maker
            role_changes.append(f"decision_maker={is_decision_maker}")
        
        if is_chef is not None:
            member.is_chef = is_chef
            role_changes.append(f"chef={is_chef}")
        
        member.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(member)
        
        APILogger.log_database_operation("UPDATE", "family_role", True, current_user.id)
        APILogger.log_user_action(current_user.id, "family_role_update", f"Updated roles for user {user_id}: {', '.join(role_changes)}")
        
        return member
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("UPDATE", "family_role", False, current_user.id)
        APILogger.log_error(f"Role update failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update family role: {str(e)}"
        )


@router.get("/search", response_model=List[UserList])
@log_endpoint("search_users")
async def search_users(
    request: Request,
    query: str = Query(..., min_length=2),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for users by name or email"""
    APILogger.log_request(request, current_user.id)
    try:
        users = db.query(User).filter(
            User.is_active == True,
            (User.first_name.ilike(f"%{query}%") |
             User.last_name.ilike(f"%{query}%") |
             User.email.ilike(f"%{query}%"))
        ).limit(10).all()
        
        APILogger.log_user_action(current_user.id, "user_search", f"Searched for users with query: {query}, found {len(users)} results")
        return users
    except Exception as e:
        APILogger.log_error(f"User search failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search users: {str(e)}"
        )


@router.get("/health/summary")
@log_endpoint("get_health_summary")
async def get_health_summary(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's health summary"""
    APILogger.log_request(request, current_user.id)
    try:
        # Get latest health record
        from app.models.user import HealthRecord
        latest_health = db.query(HealthRecord).filter(
            HealthRecord.user_id == current_user.id
        ).order_by(HealthRecord.record_date.desc()).first()
        
        # Calculate BMI
        height_m = current_user.height / 100
        bmi = current_user.weight / (height_m * height_m) if height_m > 0 else 0
        
        # Get health conditions and deficiencies
        health_conditions = []
        vitamin_deficiencies = []
        
        if current_user.health_conditions:
            try:
                health_conditions = json.loads(current_user.health_conditions)
            except:
                pass
        
        if current_user.vitamin_deficiencies:
            try:
                vitamin_deficiencies = json.loads(current_user.vitamin_deficiencies)
            except:
                pass
        
        APILogger.log_user_action(current_user.id, "health_summary_view", "Viewed health summary")
        
        return {
            "current_weight": current_user.weight,
            "current_height": current_user.height,
            "bmi": round(bmi, 2),
            "bmi_category": get_bmi_category(bmi),
            "age": current_user.age,
            "diet": current_user.diet,
            "health_conditions": health_conditions,
            "vitamin_deficiencies": vitamin_deficiencies,
            "latest_health_record": latest_health.record_date if latest_health else None
        }
    except Exception as e:
        APILogger.log_error(f"Health summary retrieval failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get health summary: {str(e)}"
        )


def get_bmi_category(bmi: float) -> str:
    """Get BMI category based on BMI value"""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


@router.get("/preferences/summary")
@log_endpoint("get_preferences_summary")
async def get_preferences_summary(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get user's preferences summary"""
    APILogger.log_request(request, current_user.id)
    try:
        preferences = {
            "meal_styles": [],
            "cuisines": [],
            "dining_style": current_user.dining_style,
            "meal_timing_preference": current_user.meal_timing_preference,
            "meal_generation_criteria": [],
            "has_special_needs": current_user.has_special_needs,
            "has_pets": current_user.has_pets,
            "religion": current_user.religion,
            "has_refrigeration": current_user.has_refrigeration,
            "needs_office_meals": current_user.needs_office_meals
        }
        
        # Parse JSON fields
        if current_user.meal_styles:
            try:
                preferences["meal_styles"] = json.loads(current_user.meal_styles)
            except:
                pass
        
        if current_user.cuisines:
            try:
                preferences["cuisines"] = json.loads(current_user.cuisines)
            except:
                pass
        
        if current_user.meal_generation_criteria:
            try:
                preferences["meal_generation_criteria"] = json.loads(current_user.meal_generation_criteria)
            except:
                pass
        
        APILogger.log_user_action(current_user.id, "preferences_summary_view", "Viewed preferences summary")
        return preferences
    except Exception as e:
        APILogger.log_error(f"Preferences summary retrieval failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences summary: {str(e)}"
        )


@router.put("/preferences/update")
@log_endpoint("update_preferences")
async def update_preferences(
    preferences: dict,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    APILogger.log_request(request, current_user.id)
    try:
        # Update preference fields
        updated_fields = []
        for field, value in preferences.items():
            if hasattr(current_user, field):
                if isinstance(value, (list, dict)):
                    setattr(current_user, field, json.dumps(value))
                else:
                    setattr(current_user, field, value)
                updated_fields.append(field)
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        APILogger.log_database_operation("UPDATE", "user_preferences", True, current_user.id)
        APILogger.log_user_action(current_user.id, "preferences_update", f"Updated preferences: {', '.join(updated_fields)}")
        
        # Clear cache
        await cache_manager.delete(f"user:{current_user.id}")
        
        return {"message": "Preferences updated successfully"}
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("UPDATE", "user_preferences", False, current_user.id)
        APILogger.log_error(f"Preferences update failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update preferences: {str(e)}"
        )
