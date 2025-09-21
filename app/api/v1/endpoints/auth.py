from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from utils.api_logger import APILogger, log_endpoint, log_user_action, log_security_event

from app.core.database import get_db
from app.core.config import settings
from app.core.cache import cache_manager
from app.models.user import User, Family, GenderEnum, DietEnum
from app.schemas.auth import (
    UserSignUp,
    UserSignUpBasic,
    UserSignIn,
    TokenResponse,
    UserProfileResponse,
    FamilyCreate,
    ProfileCompletion
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    get_current_user
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/signup", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
@log_endpoint("user_signup")
async def signup(
    user_data: UserSignUpBasic,
    request: Request,
    db: Session = Depends(get_db)
):
    """User signup with comprehensive profile creation"""
    client_ip = request.client.host if request.client else "Unknown"
    APILogger.log_request(request)
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user object with basic info
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            current_address=user_data.address,
            hashed_password=get_password_hash(user_data.password),
            profile_completed=False
        )
        
        # Save user to database
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create tokens with proper expiration
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}, 
            expires_delta=refresh_token_expires
        )
        
        # Cache user session with JSON serialization
        session_data = {
            "user_id": user.id,
            "email": user.email,
            "profile_completed": user.profile_completed,
            "signup_time": datetime.utcnow().isoformat()
        }
        session_json = json.dumps(session_data)
        session_expire = int(access_token_expires.total_seconds())
        await cache_manager.set(f"session:user:{user.id}", session_json, expire=session_expire)
        
        return UserProfileResponse(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            message="User created successfully"
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/signin", response_model=TokenResponse)
@log_endpoint("user_signin")
async def signin(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User signin with email/phone and password"""
    client_ip = request.client.host if request.client else "Unknown"
    APILogger.log_request(request)
    
    try:
        # Find user by email or phone
        user = db.query(User).filter(
            (User.email == form_data.username) | (User.phone == form_data.username)
        ).first()
        
        if not user or not verify_password(form_data.password, user.hashed_password):
            APILogger.log_auth_attempt(form_data.username, False, client_ip)
            log_security_event("Failed login attempt", ip=client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/phone or password"
            )
        
        # Create tokens with proper expiration
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}, 
            expires_delta=refresh_token_expires
        )
        
        # Cache user session with JSON serialization and proper expiration
        session_data = {
            "user_id": user.id,
            "email": user.email,
            "profile_completed": user.profile_completed,
            "login_time": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        session_json = json.dumps(session_data)
        session_expire = int(access_token_expires.total_seconds())
        await cache_manager.set(f"session:user:{user.id}", session_json, expire=session_expire)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/signup-full", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def signup_full_profile(
    user_data: UserSignUp,
    db: Session = Depends(get_db)
):
    """Complete user signup with full profile in one step"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Validate enums
        if user_data.gender and user_data.gender not in [gender.value for gender in GenderEnum]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid gender. Must be one of: {[gender.value for gender in GenderEnum]}"
            )
        
        if user_data.diet and user_data.diet not in [diet.value for diet in DietEnum]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid diet type. Must be one of: {[diet.value for diet in DietEnum]}"
            )
        
        # Create user with full profile
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            country_code=user_data.country_code,
            current_address=user_data.current_address,
            height=user_data.height,
            weight=user_data.weight,
            age=user_data.age,
            gender=user_data.gender,
            diet=user_data.diet,
            hashed_password=get_password_hash(user_data.password),
            profile_completed=True
        )
        
        # Save user to database
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create tokens with proper expiration
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}, 
            expires_delta=refresh_token_expires
        )
        
        # Cache user session with JSON serialization
        session_data = {
            "user_id": user.id,
            "email": user.email,
            "profile_completed": user.profile_completed,
            "signup_time": datetime.utcnow().isoformat(),
            "signup_method": "full_profile"
        }
        session_json = json.dumps(session_data)
        session_expire = int(access_token_expires.total_seconds())
        await cache_manager.set(f"session:user:{user.id}", session_json, expire=session_expire)
        
        return UserProfileResponse(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            message="User created with full profile successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token and get user
        user_id = get_current_user(refresh_token)
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user_id=user.id,
            message="Token refreshed successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
@log_endpoint("user_logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """User logout - invalidate session"""
    client_ip = request.client.host if request.client else "Unknown"
    
    try:
        # Remove user session from cache
        await cache_manager.delete(f"session:user:{current_user.id}")
        
        log_user_action("User Logout", current_user.id, f"IP: {client_ip}")
        return {"message": "Logout successful"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.post("/complete-profile", response_model=UserProfileResponse)
@log_endpoint("complete_profile")
async def complete_profile(
    profile_data: ProfileCompletion,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete mandatory user profile information"""
    try:
        # Update user with mandatory profile data
        current_user.phone = profile_data.phone
        current_user.country_code = profile_data.country_code
        current_user.height = profile_data.height
        current_user.weight = profile_data.weight
        current_user.age = profile_data.age
        
        # Validate gender enum
        if profile_data.gender and profile_data.gender not in [gender.value for gender in GenderEnum]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid gender. Must be one of: {[gender.value for gender in GenderEnum]}"
            )
        current_user.gender = profile_data.gender
        
        # Update address details
        current_user.current_postal_code = profile_data.current_postal_code
        current_user.current_city = profile_data.current_city
        current_user.current_country = profile_data.current_country
        current_user.native_address = profile_data.native_address
        current_user.native_postal_code = profile_data.native_postal_code
        current_user.native_city = profile_data.native_city
        current_user.native_country = profile_data.native_country
        
        # Update diet and preferences with enum validation
        if profile_data.diet and profile_data.diet not in [diet.value for diet in DietEnum]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid diet type. Must be one of: {[diet.value for diet in DietEnum]}"
            )
        current_user.diet = profile_data.diet
        
        if profile_data.preferred_meats:
            current_user.preferred_meats = json.dumps(profile_data.preferred_meats)
        current_user.cuisines = json.dumps(profile_data.cuisines)
        
        # Handle family account setup
        if profile_data.is_family_account and profile_data.family_name:
            family = Family(
                name=profile_data.family_name,
                meal_frequency=3,  # default
                meal_timings=json.dumps(["08:00", "13:00", "19:00"])  # default
            )
            db.add(family)
            db.flush()
            
            current_user.family_id = family.id
            current_user.is_family_account = True
            current_user.is_decision_maker = True
        
        # Mark profile as completed
        current_user.profile_completed = True
        
        db.commit()
        db.refresh(current_user)
        
        APILogger.log_database_operation("UPDATE", "users", True, current_user.id)
        log_user_action("Profile Completion", current_user.id, "Full profile completed")
        
        return UserProfileResponse(
            user=current_user,
            message="Profile completed successfully"
        )
        
    except Exception as e:
        db.rollback()
        APILogger.log_database_operation("UPDATE", "users", False, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete profile: {str(e)}"
        )


@router.get("/me", response_model=UserProfileResponse)
@log_endpoint("get_user_profile")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        db.refresh(current_user)
        return UserProfileResponse(
            user=current_user,
            message="Profile retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.post("/signin-json", response_model=TokenResponse)
async def signin_with_json(
    signin_data: UserSignIn,
    db: Session = Depends(get_db)
):
    """Alternative signin endpoint using JSON body instead of form data"""
    try:
        # Find user by email or phone
        user = db.query(User).filter(
            (User.email == signin_data.email_or_phone) | (User.phone == signin_data.email_or_phone)
        ).first()
        
        if not user or not verify_password(signin_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/phone or password"
            )
        
        # Create tokens with proper expiration
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}, 
            expires_delta=refresh_token_expires
        )
        
        # Cache user session with JSON serialization
        session_data = {
            "user_id": user.id,
            "email": user.email,
            "profile_completed": user.profile_completed,
            "login_time": datetime.utcnow().isoformat(),
            "signin_method": "json"
        }
        session_json = json.dumps(session_data)
        session_expire = int(access_token_expires.total_seconds())
        await cache_manager.set(f"session:user:{user.id}", session_json, expire=session_expire)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id,
            message="Login successful via JSON"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/add-family-member")
async def add_family_member(
    family_data: FamilyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new member to existing family"""
    try:
        if not current_user.is_family_account or not current_user.is_decision_maker:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only family decision makers can add members"
            )
        
        # Create new family member
        member_data = family_data.dict()
        member_data["family_id"] = current_user.family_id
        member_data["is_family_account"] = True
        
        # Hash password
        member_data["password_hash"] = get_password_hash(family_data.password)
        del member_data["password"]
        
        new_member = User(**member_data)
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        
        return {
            "message": "Family member added successfully",
            "member_id": new_member.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add family member: {str(e)}"
        )
