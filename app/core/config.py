from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Money - Health Food App"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/app.db"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    
    # AI Service
    AI_SERVICE_URL: str = "http://localhost:8001"
    WEAVIATE_URL: str = "http://localhost:8080"
    
    # External Services (for future use)
    CLIMATE_API_KEY: Optional[str] = None
    HEALTH_APP_WEBHOOK: Optional[str] = None
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:19006",
        "http://localhost:19000"
    ]
    
    # Mock Data (for local testing)
    MOCK_CLIMATE_DATA: bool = True
    MOCK_PRICE_DATA: bool = True
    MOCK_HEALTH_SYNC: bool = True
    
    # AI Model Settings
    MODEL_CACHE_DIR: str = "./models"
    USE_LOCAL_MODELS: bool = True
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7
    
    # Notification Settings
    ENABLE_EMAIL_NOTIFICATIONS: bool = False
    ENABLE_PUSH_NOTIFICATIONS: bool = False
    ENABLE_SMS_NOTIFICATIONS: bool = False
    
    # Meal Generation
    DEFAULT_MEAL_GENERATION_TIME: str = "18:00"  # 6 PM
    MAX_MEAL_REGENERATIONS: int = 3
    STOCK_PRIORITY_THRESHOLD: float = 0.2  # 20% of minimum stock
    
    # Health Tracking
    ENABLE_HEALTH_SYNC: bool = True
    NUTRIENT_TRACKING: bool = True
    CALORIE_CALCULATION: bool = True
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
os.makedirs("./data", exist_ok=True)

