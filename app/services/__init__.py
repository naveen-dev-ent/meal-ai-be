"""
Services package for the Money-Health application.

This package contains all business logic services including:
- Meal generation and management
- Stock management and analytics
- User authentication and profile management
- Health tracking and recommendations
- AI-powered meal planning strategies
"""

from .meal_service import MealService
from .stock_service import StockService
from .strategies import (
    MealGenerationStrategy,
    HealthFocusedStrategy,
    BudgetOptimizedStrategy,
    StockUtilizationStrategy,
    MealGenerationStrategyFactory,
)

# Import service interfaces and base classes
try:
    from app.core.base import (
        ServiceInterface,
        CacheInterface,
        NotificationInterface,
        AIServiceInterface,
    )
except ImportError:
    # Fallback if base interfaces are not available
    ServiceInterface = object
    CacheInterface = object
    NotificationInterface = object
    AIServiceInterface = object

__all__ = [
    # Core services
    "MealService",
    "StockService",
    
    # Strategy pattern implementations
    "MealGenerationStrategy",
    "HealthFocusedStrategy", 
    "BudgetOptimizedStrategy",
    "StockUtilizationStrategy",
    "MealGenerationStrategyFactory",
    
    # Service interfaces
    "ServiceInterface",
    "CacheInterface",
    "NotificationInterface",
    "AIServiceInterface",
]
