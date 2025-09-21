"""
Strategy pattern implementation for meal generation algorithms.

This module provides different strategies for generating meals based on
various criteria like health focus, budget optimization, or stock utilization.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import date
import random

from app.core.base import Priority, Result
from app.models.user import User, Stock
from app.schemas.meals import MealGenerationRequest


class MealGenerationStrategy(ABC):
    """
    Abstract base class for meal generation strategies.
    
    This class defines the interface that all meal generation strategies
    must implement, allowing for different algorithms to be used
    interchangeably.
    """

    @abstractmethod
    async def generate_meals(
        self,
        user: User,
        stock_items: List[Stock],
        request: MealGenerationRequest,
    ) -> Result:
        """
        Generate meals using this strategy.
        
        Args:
            user: User for whom to generate meals
            stock_items: Available stock items
            request: Meal generation request parameters
            
        Returns:
            Result containing generated meals or error information
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass

    @abstractmethod
    def get_priority(self) -> Priority:
        """Get the priority level of this strategy."""
        pass


class HealthFocusedStrategy(MealGenerationStrategy):
    """
    Strategy for generating meals focused on health and nutrition.
    
    This strategy prioritizes nutritional balance, health conditions,
    and dietary restrictions over other factors.
    """

    def __init__(self):
        self.name = "Health Focused"
        self.priority = Priority.HIGH

    async def generate_meals(
        self,
        user: User,
        stock_items: List[Stock],
        request: MealGenerationRequest,
    ) -> Result:
        """Generate health-focused meals."""
        try:
            # Filter stock items by health benefits
            healthy_stock = self._filter_healthy_stock(stock_items, user)
            
            if not healthy_stock:
                return Result.failure_result(
                    "No healthy stock items available for meal generation"
                )

            # Generate meals based on health criteria
            meals = await self._create_health_optimized_meals(
                user, healthy_stock, request
            )

            return Result.success_result(
                data=meals,
                message=f"Generated {len(meals)} health-focused meals"
            )

        except Exception as e:
            return Result.failure_result(f"Health strategy failed: {str(e)}")

    def _filter_healthy_stock(
        self, stock_items: List[Stock], user: User
    ) -> List[Stock]:
        """Filter stock items based on health criteria."""
        healthy_items = []

        for item in stock_items:
            if self._is_healthy_item(item, user):
                healthy_items.append(item)

        return healthy_items

    def _is_healthy_item(self, item: Stock, user: User) -> bool:
        """Check if a stock item is healthy for the user."""
        # Check for high nutritional value
        if item.calories_per_100g and item.calories_per_100g > 300:
            return False  # Too high in calories

        # Check for protein content (good for health)
        if item.protein_per_100g and item.protein_per_100g > 20:
            return True

        # Check for low fat content
        if item.fat_per_100g and item.fat_per_100g < 5:
            return True

        # Check for fiber content
        if hasattr(item, 'fiber_per_100g') and item.fiber_per_100g > 3:
            return True

        return False

    async def _create_health_optimized_meals(
        self,
        user: User,
        healthy_stock: List[Stock],
        request: MealGenerationRequest,
    ) -> List[Dict[str, Any]]:
        """Create meals optimized for health."""
        meals = []
        meal_types = request.meal_types or ["breakfast", "lunch", "dinner"]

        for meal_type in meal_types:
            meal = await self._create_single_health_meal(
                meal_type, user, healthy_stock
            )
            if meal:
                meals.append(meal)

        return meals

    async def _create_single_health_meal(
        self, meal_type: str, user: User, healthy_stock: List[Stock]
    ) -> Optional[Dict[str, Any]]:
        """Create a single health-optimized meal."""
        # Select ingredients based on health criteria
        selected_ingredients = self._select_healthy_ingredients(
            healthy_stock, meal_type
        )

        if not selected_ingredients:
            return None

        # Calculate nutritional totals
        nutrition = self._calculate_nutrition(selected_ingredients)

        return {
            "name": f"Healthy {meal_type.title()}",
            "meal_type": meal_type,
            "ingredients": selected_ingredients,
            "nutrition": nutrition,
            "health_score": self._calculate_health_score(nutrition),
            "strategy": self.get_strategy_name(),
        }

    def _select_healthy_ingredients(
        self, healthy_stock: List[Stock], meal_type: str
    ) -> List[Dict[str, Any]]:
        """Select healthy ingredients for the meal."""
        ingredients = []
        max_ingredients = 5 if meal_type == "dinner" else 3

        # Prioritize high-protein items
        protein_items = [
            item for item in healthy_stock
            if item.protein_per_100g and item.protein_per_100g > 15
        ]

        # Prioritize low-calorie vegetables
        vegetable_items = [
            item for item in healthy_stock
            if item.calories_per_100g and item.calories_per_100g < 100
        ]

        # Select ingredients
        if protein_items:
            protein_item = random.choice(protein_items)
            ingredients.append({
                "name": protein_item.item_name,
                "quantity": 100,
                "unit": "g",
                "stock_id": protein_item.id,
            })

        if vegetable_items:
            veg_count = min(2, len(vegetable_items))
            selected_veggies = random.sample(vegetable_items, veg_count)
            for veg in selected_veggies:
                ingredients.append({
                    "name": veg.item_name,
                    "quantity": 50,
                    "unit": "g",
                    "stock_id": veg.id,
                })

        return ingredients[:max_ingredients]

    def _calculate_nutrition(self, ingredients: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate total nutrition for ingredients."""
        nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

        for ingredient in ingredients:
            # This would need to be implemented with actual nutritional data
            # For now, using mock values
            nutrition["calories"] += 150
            nutrition["protein"] += 8
            nutrition["carbs"] += 20
            nutrition["fat"] += 3

        return nutrition

    def _calculate_health_score(self, nutrition: Dict[str, float]) -> float:
        """Calculate a health score for the meal."""
        score = 100

        # Deduct points for high calories
        if nutrition["calories"] > 500:
            score -= 20

        # Add points for high protein
        if nutrition["protein"] > 25:
            score += 15

        # Deduct points for high fat
        if nutrition["fat"] > 15:
            score -= 10

        return max(0, min(100, score))

    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return self.name

    def get_priority(self) -> Priority:
        """Get the priority level of this strategy."""
        return self.priority


class BudgetOptimizedStrategy(MealGenerationStrategy):
    """
    Strategy for generating meals optimized for budget constraints.
    
    This strategy prioritizes cost-effectiveness while maintaining
    basic nutritional requirements.
    """

    def __init__(self):
        self.name = "Budget Optimized"
        self.priority = Priority.MEDIUM

    async def generate_meals(
        self,
        user: User,
        stock_items: List[Stock],
        request: MealGenerationRequest,
    ) -> Result:
        """Generate budget-optimized meals."""
        try:
            # Filter stock items by cost
            affordable_stock = self._filter_affordable_stock(stock_items, user)

            if not affordable_stock:
                return Result.failure_result(
                    "No affordable stock items available for meal generation"
                )

            # Generate meals based on budget criteria
            meals = await self._create_budget_optimized_meals(
                user, affordable_stock, request
            )

            return Result.success_result(
                data=meals,
                message=f"Generated {len(meals)} budget-optimized meals"
            )

        except Exception as e:
            return Result.failure_result(f"Budget strategy failed: {str(e)}")

    def _filter_affordable_stock(
        self, stock_items: List[Stock], user: User
    ) -> List[Stock]:
        """Filter stock items based on affordability."""
        affordable_items = []

        for item in stock_items:
            if self._is_affordable_item(item, user):
                affordable_items.append(item)

        return affordable_items

    def _is_affordable_item(self, item: Stock, user: User) -> bool:
        """Check if a stock item is affordable for the user."""
        # Check if item has price information
        if not item.price_per_unit:
            return True  # Assume affordable if no price info

        # Define affordability thresholds based on user budget
        daily_budget = getattr(user, 'daily_food_budget', 20.0)  # Default $20
        max_item_price = daily_budget * 0.3  # Max 30% of daily budget per item

        return item.price_per_unit <= max_item_price

    async def _create_budget_optimized_meals(
        self,
        user: User,
        affordable_stock: List[Stock],
        request: MealGenerationRequest,
    ) -> List[Dict[str, Any]]:
        """Create meals optimized for budget."""
        meals = []
        meal_types = request.meal_types or ["breakfast", "lunch", "dinner"]

        for meal_type in meal_types:
            meal = await self._create_single_budget_meal(
                meal_type, user, affordable_stock
            )
            if meal:
                meals.append(meal)

        return meals

    async def _create_single_budget_meal(
        self, meal_type: str, user: User, affordable_stock: List[Stock]
    ) -> Optional[Dict[str, Any]]:
        """Create a single budget-optimized meal."""
        # Select ingredients based on cost
        selected_ingredients = self._select_affordable_ingredients(
            affordable_stock, meal_type
        )

        if not selected_ingredients:
            return None

        # Calculate cost and nutrition
        total_cost = self._calculate_total_cost(selected_ingredients)
        nutrition = self._calculate_nutrition(selected_ingredients)

        return {
            "name": f"Budget {meal_type.title()}",
            "meal_type": meal_type,
            "ingredients": selected_ingredients,
            "nutrition": nutrition,
            "total_cost": total_cost,
            "cost_per_meal": total_cost,
            "strategy": self.get_strategy_name(),
        }

    def _select_affordable_ingredients(
        self, affordable_stock: List[Stock], meal_type: str
    ) -> List[Dict[str, Any]]:
        """Select affordable ingredients for the meal."""
        ingredients = []
        max_ingredients = 4 if meal_type == "dinner" else 3

        # Sort by price (lowest first)
        sorted_stock = sorted(
            affordable_stock,
            key=lambda x: x.price_per_unit or 0
        )

        # Select cheapest ingredients
        for i, item in enumerate(sorted_stock[:max_ingredients]):
            quantity = 100 if i == 0 else 50  # Main ingredient gets more
            ingredients.append({
                "name": item.item_name,
                "quantity": quantity,
                "unit": "g",
                "stock_id": item.id,
                "price_per_unit": item.price_per_unit,
            })

        return ingredients

    def _calculate_total_cost(self, ingredients: List[Dict[str, Any]]) -> float:
        """Calculate total cost for ingredients."""
        total_cost = 0.0

        for ingredient in ingredients:
            price = ingredient.get("price_per_unit", 0)
            quantity = ingredient.get("quantity", 0)
            if price and quantity:
                total_cost += (price * quantity) / 1000  # Convert to per-gram

        return round(total_cost, 2)

    def _calculate_nutrition(self, ingredients: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate total nutrition for ingredients."""
        nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}

        for ingredient in ingredients:
            # Mock nutritional values
            nutrition["calories"] += 120
            nutrition["protein"] += 6
            nutrition["carbs"] += 18
            nutrition["fat"] += 2

        return nutrition

    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return self.name

    def get_priority(self) -> Priority:
        """Get the priority level of this strategy."""
        return self.priority


class StockUtilizationStrategy(MealGenerationStrategy):
    """
    Strategy for generating meals that maximize stock utilization.
    
    This strategy prioritizes using available stock items efficiently,
    especially those close to expiry.
    """

    def __init__(self):
        self.name = "Stock Utilization"
        self.priority = Priority.MEDIUM

    async def generate_meals(
        self,
        user: User,
        stock_items: List[Stock],
        request: MealGenerationRequest,
    ) -> Result:
        """Generate stock utilization optimized meals."""
        try:
            # Prioritize stock items by expiry and quantity
            prioritized_stock = self._prioritize_stock_items(stock_items)

            if not prioritized_stock:
                return Result.failure_result(
                    "No stock items available for meal generation"
                )

            # Generate meals based on stock utilization
            meals = await self._create_stock_utilization_meals(
                user, prioritized_stock, request
            )

            return Result.success_result(
                data=meals,
                message=f"Generated {len(meals)} stock utilization meals"
            )

        except Exception as e:
            return Result.failure_result(f"Stock utilization strategy failed: {str(e)}")

    def _prioritize_stock_items(self, stock_items: List[Stock]) -> List[Stock]:
        """Prioritize stock items by expiry and quantity."""
        prioritized = []

        for item in stock_items:
            priority_score = self._calculate_stock_priority(item)
            prioritized.append((item, priority_score))

        # Sort by priority score (highest first)
        prioritized.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in prioritized]

    def _calculate_stock_priority(self, item: Stock) -> float:
        """Calculate priority score for a stock item."""
        score = 0.0

        # High priority for items close to expiry
        if item.expiry_date:
            days_until_expiry = (item.expiry_date - date.today()).days
            if days_until_expiry <= 1:
                score += 100  # Critical
            elif days_until_expiry <= 3:
                score += 80   # High
            elif days_until_expiry <= 7:
                score += 60   # Medium

        # Priority for low stock items
        if item.current_quantity <= item.minimum_quantity:
            score += 50

        # Priority for perishable items
        if getattr(item, 'is_perishable', False):
            score += 30

        # Priority for special care items
        if getattr(item, 'is_special_care_item', False):
            score += 40

        return score

    async def _create_stock_utilization_meals(
        self,
        user: User,
        prioritized_stock: List[Stock],
        request: MealGenerationRequest,
    ) -> List[Dict[str, Any]]:
        """Create meals optimized for stock utilization."""
        meals = []
        meal_types = request.meal_types or ["breakfast", "lunch", "dinner"]

        for meal_type in meal_types:
            meal = await self._create_single_stock_meal(
                meal_type, user, prioritized_stock
            )
            if meal:
                meals.append(meal)

        return meals

    async def _create_single_stock_meal(
        self, meal_type: str, user: User, prioritized_stock: List[Stock]
    ) -> Optional[Dict[str, Any]]:
        """Create a single stock utilization meal."""
        # Select ingredients based on stock priority
        selected_ingredients = self._select_stock_ingredients(
            prioritized_stock, meal_type
        )

        if not selected_ingredients:
            return None

        # Calculate stock utilization metrics
        utilization_metrics = self._calculate_utilization_metrics(selected_ingredients)

        return {
            "name": f"Stock {meal_type.title()}",
            "meal_type": meal_type,
            "ingredients": selected_ingredients,
            "utilization_metrics": utilization_metrics,
            "strategy": self.get_strategy_name(),
        }

    def _select_stock_ingredients(
        self, prioritized_stock: List[Stock], meal_type: str
    ) -> List[Dict[str, Any]]:
        """Select ingredients based on stock priority."""
        ingredients = []
        max_ingredients = 5 if meal_type == "dinner" else 3

        # Use highest priority items first
        for i, item in enumerate(prioritized_stock[:max_ingredients]):
            quantity = min(100, item.current_quantity)  # Don't exceed available
            ingredients.append({
                "name": item.item_name,
                "quantity": quantity,
                "unit": item.unit,
                "stock_id": item.id,
                "current_quantity": item.current_quantity,
                "expiry_date": item.expiry_date,
            })

        return ingredients

    def _calculate_utilization_metrics(
        self, ingredients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate stock utilization metrics."""
        total_items = len(ingredients)
        expiring_soon = 0
        low_stock = 0

        for ingredient in ingredients:
            if ingredient.get("expiry_date"):
                days_until_expiry = (ingredient["expiry_date"] - date.today()).days
                if days_until_expiry <= 3:
                    expiring_soon += 1

            current_qty = ingredient.get("current_quantity", 0)
            if current_qty <= 50:  # Assuming 50g is low stock
                low_stock += 1

        return {
            "total_items_used": total_items,
            "expiring_soon_items": expiring_soon,
            "low_stock_items": low_stock,
            "utilization_score": (expiring_soon + low_stock) / total_items * 100,
        }

    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return self.name

    def get_priority(self) -> Priority:
        """Get the priority level of this strategy."""
        return self.priority


class MealGenerationStrategyFactory:
    """
    Factory class for creating meal generation strategies.
    
    This class implements the Factory pattern to create and configure
    different meal generation strategies based on user preferences.
    """

    def __init__(self):
        self._strategies = {
            "health": HealthFocusedStrategy(),
            "budget": BudgetOptimizedStrategy(),
            "stock": StockUtilizationStrategy(),
        }

    def get_strategy(self, strategy_name: str) -> MealGenerationStrategy:
        """
        Get a meal generation strategy by name.
        
        Args:
            strategy_name: Name of the strategy to retrieve
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy name is not recognized
        """
        if strategy_name not in self._strategies:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        return self._strategies[strategy_name]

    def get_all_strategies(self) -> List[MealGenerationStrategy]:
        """Get all available strategies."""
        return list(self._strategies.values())

    def get_strategy_by_priority(self, priority: Priority) -> List[MealGenerationStrategy]:
        """Get strategies by priority level."""
        return [
            strategy for strategy in self._strategies.values()
            if strategy.get_priority() == priority
        ]

    def get_available_strategies(self) -> List[str]:
        """Get names of all available strategies."""
        return list(self._strategies.keys())
