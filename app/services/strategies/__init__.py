"""
Strategy pattern implementations for the application.

This package provides various strategy implementations for different
business logic scenarios like meal generation, stock management, etc.
"""

from .meal_generation_strategy import (
    MealGenerationStrategy,
    HealthFocusedStrategy,
    BudgetOptimizedStrategy,
    StockUtilizationStrategy,
    MealGenerationStrategyFactory,
)

__all__ = [
    "MealGenerationStrategy",
    "HealthFocusedStrategy",
    "BudgetOptimizedStrategy",
    "StockUtilizationStrategy",
    "MealGenerationStrategyFactory",
]
