"""
Refactored meal service using strategy pattern and dependency injection.

This service now follows SOLID principles and uses the strategy pattern
for different meal generation algorithms.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import date, datetime
import logging

from app.core.base import (
    ServiceInterface,
    CacheInterface,
    NotificationInterface,
    AIServiceInterface,
    Result,
    Priority,
)
from app.models.user import User, Meal, Stock
from app.schemas.meals import (
    MealGenerationRequest,
    MealGenerationResponse,
    MealResponse,
)
from app.services.strategies import MealGenerationStrategyFactory
from app.services.strategies.meal_generation_strategy import MealGenerationStrategy


logger = logging.getLogger(__name__)


class MealService(ServiceInterface[Meal, Any, Any, MealResponse]):
    """
    Refactored service for AI-powered meal generation and management.
    
    This service now uses the strategy pattern for different meal generation
    algorithms and follows dependency injection principles.
    """

    def __init__(
        self,
        cache_service: CacheInterface,
        ai_service: AIServiceInterface,
        notification_service: NotificationInterface,
    ):
        self.cache_service = cache_service
        self.ai_service = ai_service
        self.notification_service = notification_service
        self.strategy_factory = MealGenerationStrategyFactory()
        """
        Initialize the meal service with dependencies.
        
        Args:
            cache_service: Cache service for storing meal data
            ai_service: AI service for intelligent meal generation
            notification_service: Service for sending notifications
        """
        self.cache_service = cache_service
        self.ai_service = ai_service
        self.notification_service = notification_service
        self.strategy_factory = MealGenerationStrategyFactory()
        
        # Mock meal templates for local testing
        self.meal_templates = self._load_meal_templates()
        
        # Mock nutritional data
        self.nutritional_data = self._load_nutritional_data()

    async def create(
        self, obj_in: Any, db: Session, **kwargs
    ) -> MealResponse:
        """Create a new meal."""
        try:
            # Implementation for creating meals
            pass
        except Exception as e:
            logger.error(f"Failed to create meal: {str(e)}")
            raise

    async def get(self, id: int, db: Session) -> Optional[MealResponse]:
        """Get a meal by ID."""
        try:
            # Implementation for getting meals
            pass
        except Exception as e:
            logger.error(f"Failed to get meal {id}: {str(e)}")
            raise

    async def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[MealResponse]:
        """Get multiple meals with pagination."""
        try:
            # Implementation for getting multiple meals
            pass
        except Exception as e:
            logger.error(f"Failed to get meals: {str(e)}")
            raise

    async def update(
        self, id: int, obj_in: Any, db: Session, **kwargs
    ) -> Optional[MealResponse]:
        """Update an existing meal."""
        try:
            # Implementation for updating meals
            pass
        except Exception as e:
            logger.error(f"Failed to update meal {id}: {str(e)}")
            raise

    async def delete(self, id: int, db: Session) -> bool:
        """Delete a meal by ID."""
        try:
            # Implementation for deleting meals
            pass
        except Exception as e:
            logger.error(f"Failed to delete meal {id}: {str(e)}")
            raise

    async def generate_meals(
        self, 
        generation_request: MealGenerationRequest, 
        db: Session
    ) -> Result:
        """
        Generate AI-powered meal suggestions using strategy pattern.
        
        Args:
            generation_request: Request containing generation parameters
            db: Database session
            
        Returns:
            Result containing generated meals or error information
        """
        try:
            # Get user/family preferences
            user = await self._get_user(generation_request, db)
            if not user:
                return Result.failure_result("User not found")

            # Get available stock
            stock_items = await self._get_available_stock(generation_request, db)
            
            # Determine strategy based on user preferences
            strategy = self._select_generation_strategy(generation_request, user)
            
            # Generate meals using selected strategy
            result = await strategy.generate_meals(user, stock_items, generation_request)
            
            if result.success:
                # Cache the generated meals
                await self._cache_generated_meals(
                    generation_request.user_id or generation_request.family_id,
                    result.data
                )
                
                # Send notification if enabled
                await self._send_generation_notification(user, result.data)
            
            return result

        except Exception as e:
            logger.error(f"Failed to generate meals: {str(e)}")
            return Result.failure_result(f"Meal generation failed: {str(e)}")

    async def _get_user(
        self, generation_request: MealGenerationRequest, db: Session
    ) -> Optional[User]:
        """Get user for meal generation."""
        if generation_request.user_id:
            return db.query(User).filter(User.id == generation_request.user_id).first()
        elif generation_request.family_id:
            return db.query(User).filter(User.family_id == generation_request.family_id).first()
        return None

    async def _get_available_stock(
        self, generation_request: MealGenerationRequest, db: Session
    ) -> List[Stock]:
        """Get available stock items for meal generation."""
        query = db.query(Stock)
        
        if generation_request.family_id:
            query = query.filter(Stock.family_id == generation_request.family_id)
        else:
            query = query.filter(Stock.user_id == generation_request.user_id)
        
        # Filter by generation criteria
        if generation_request.use_stock:
            query = query.filter(Stock.current_quantity > 0)
        
        if generation_request.prioritize_expiry:
            query = query.filter(Stock.expiry_date.isnot(None))
            query = query.order_by(Stock.expiry_date)
        
        return query.all()

    def _select_generation_strategy(
        self, generation_request: MealGenerationRequest, user: User
    ) -> MealGenerationStrategy:
        """Select the appropriate meal generation strategy."""
        # Check user preferences for strategy selection
        if hasattr(user, 'meal_generation_criteria'):
            try:
                criteria = json.loads(user.meal_generation_criteria)
                
                # Health-focused strategy for users with health conditions
                if criteria.get('health_focused', False):
                    return self.strategy_factory.get_strategy("health")
                
                # Budget-optimized strategy for users with budget constraints
                if criteria.get('budget_optimized', False):
                    return self.strategy_factory.get_strategy("budget")
                
                # Stock utilization strategy for users with stock management focus
                if criteria.get('stock_utilization', False):
                    return self.strategy_factory.get_strategy("stock")
                    
            except (json.JSONDecodeError, AttributeError):
                logger.warning("Invalid meal generation criteria format")
        
        # Default to health-focused strategy
        return self.strategy_factory.get_strategy("health")

    async def _cache_generated_meals(self, user_id: int, meals: List[Dict[str, Any]]):
        """Cache generated meals for quick retrieval."""
        try:
            cache_key = f"generated_meals:{user_id}:{date.today().isoformat()}"
            await self.cache_service.set(cache_key, meals, expire=86400)  # 24 hours
        except Exception as e:
            logger.warning(f"Failed to cache generated meals: {str(e)}")

    async def _send_generation_notification(
        self, user: User, meals: List[Dict[str, Any]]
    ):
        """Send notification about generated meals."""
        try:
            message = f"Generated {len(meals)} meals for {user.name}"
            await self.notification_service.send(
                recipient=user.email or user.mobile_number,
                message=message,
                notification_type="meal_generation"
            )
        except Exception as e:
            logger.warning(f"Failed to send meal generation notification: {str(e)}")

    async def _generate_single_meal(
        self,
        meal_type: str,
        date: date,
        user: User,
        stock_items: List[Stock],
        generation_request: MealGenerationRequest
    ) -> Optional[MealResponse]:
        """Generate a single meal based on type and preferences."""
        try:
            # Get meal template
            template = self._get_meal_template(meal_type, user)
            if not template:
                return None
            
            # Adapt template based on available stock
            adapted_meal = self._adapt_meal_to_stock(template, stock_items, user)
            
            # Create meal object
            meal = Meal(
                name=adapted_meal['name'],
                description=adapted_meal['description'],
                meal_type=meal_type,
                planned_date=date,
                planned_time=self._get_meal_time(meal_type, user),
                total_calories=adapted_meal['calories'],
                total_protein=adapted_meal['protein'],
                total_carbs=adapted_meal['carbs'],
                total_fat=adapted_meal['fat'],
                ingredients=json.dumps(adapted_meal['ingredients']),
                cooking_instructions=adapted_meal['cooking_instructions'],
                is_special_care_meal=user.has_special_needs,
                is_office_meal=generation_request.is_office_meal,
                is_guest_meal=generation_request.include_guests,
                status="planned",
                is_approved=False
            )
            
            return meal
            
        except Exception as e:
            logger.error(f"Error generating meal for {meal_type}: {str(e)}")
            return None

    def _get_meal_template(self, meal_type: str, user: User) -> Optional[Dict[str, Any]]:
        """Get a meal template based on type and user preferences."""
        # Filter templates by meal type and user preferences
        available_templates = [
            template for template in self.meal_templates 
            if template['meal_type'] == meal_type
        ]
        
        if not available_templates:
            return None
        
        # Filter by diet restrictions
        available_templates = self._filter_by_diet(available_templates, user)
        
        # Filter by cuisine preferences
        available_templates = self._filter_by_cuisine(available_templates, user)
        
        # Return random template if available
        if available_templates:
            return random.choice(available_templates)
        
        return None

    def _filter_by_diet(
        self, templates: List[Dict[str, Any]], user: User
    ) -> List[Dict[str, Any]]:
        """Filter templates by user's dietary restrictions."""
        if user.diet == 'vegetarian':
            return [
                t for t in templates 
                if not any(ingredient in str(t).lower() 
                          for ingredient in ['meat', 'chicken', 'beef', 'fish'])
            ]
        elif user.diet == 'vegan':
            return [
                t for t in templates 
                if not any(ingredient in str(t).lower() 
                          for ingredient in ['meat', 'chicken', 'beef', 'fish', 'dairy', 'eggs'])
            ]
        
        return templates

    def _filter_by_cuisine(
        self, templates: List[Dict[str, Any]], user: User
    ) -> List[Dict[str, Any]]:
        """Filter templates by user's cuisine preferences."""
        if not user.cuisines:
            return templates
        
        try:
            user_cuisines = json.loads(user.cuisines)
            return [
                t for t in templates
                if t.get('cuisine') in user_cuisines
            ]
        except (json.JSONDecodeError, AttributeError):
            logger.warning("Invalid cuisine preferences format")
            return templates

    def _adapt_meal_to_stock(
        self, 
        template: Dict[str, Any], 
        stock_items: List[Stock], 
        user: User
    ) -> Dict[str, Any]:
        """Adapt meal template to available stock."""
        adapted_meal = template.copy()
        
        # Check which ingredients are available
        available_ingredients = []
        missing_ingredients = []
        
        for ingredient in template['ingredients']:
            # Find matching stock item
            stock_item = next(
                (item for item in stock_items 
                 if item.item_name.lower() in ingredient['name'].lower() or 
                    ingredient['name'].lower() in item.item_name.lower()),
                None
            )
            
            if stock_item and stock_item.current_quantity >= ingredient['quantity']:
                available_ingredients.append({
                    'name': stock_item.item_name,
                    'quantity': ingredient['quantity'],
                    'unit': ingredient['unit'],
                    'stock_id': stock_item.id
                })
            else:
                missing_ingredients.append(ingredient)
        
        # Update ingredients list
        adapted_meal['ingredients'] = available_ingredients + missing_ingredients
        
        # Adjust nutritional values based on available ingredients
        adapted_meal = self._recalculate_nutrition(adapted_meal, available_ingredients, stock_items)
        
        return adapted_meal

    def _recalculate_nutrition(
        self, 
        meal: Dict[str, Any], 
        available_ingredients: List[Dict], 
        stock_items: List[Stock]
    ) -> Dict[str, Any]:
        """Recalculate nutritional values based on available ingredients."""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for ingredient in available_ingredients:
            stock_item = next(
                (item for item in stock_items if item.id == ingredient['stock_id']),
                None
            )
            
            if stock_item:
                # Calculate nutrition based on quantity
                quantity_ratio = ingredient['quantity'] / 100  # Convert to 100g ratio
                
                total_calories += (stock_item.calories_per_100g or 0) * quantity_ratio
                total_protein += (stock_item.protein_per_100g or 0) * quantity_ratio
                total_carbs += (stock_item.carbs_per_100g or 0) * quantity_ratio
                total_fat += (stock_item.fat_per_100g or 0) * quantity_ratio
        
        meal['calories'] = round(total_calories, 1)
        meal['protein'] = round(total_protein, 1)
        meal['carbs'] = round(total_carbs, 1)
        meal['fat'] = round(total_fat, 1)
        
        return meal

    def _get_meal_time(self, meal_type: str, user: User) -> str:
        """Get preferred meal time based on user preferences."""
        if user.meal_timing_preference:
            return user.meal_timing_preference
        
        # Default meal times
        default_times = {
            'breakfast': '08:00',
            'lunch': '13:00',
            'dinner': '19:00',
            'snack': '15:00'
        }
        
        return default_times.get(meal_type, '18:00')

    def _calculate_total_nutrition(self, meals: List[MealResponse]) -> Dict[str, float]:
        """Calculate total nutritional values across all meals."""
        totals = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0
        }
        
        for meal in meals:
            totals['calories'] += meal.total_calories or 0
            totals['protein'] += meal.total_protein or 0
            totals['carbs'] += meal.total_carbs or 0
            totals['fat'] += meal.total_fat or 0
        
        return totals

    def _determine_shopping_list(
        self, 
        meals: List[MealResponse], 
        stock_items: List[Stock]
    ) -> List[str]:
        """Determine items that need to be purchased."""
        shopping_list = []
        
        for meal in meals:
            if meal.ingredients:
                try:
                    ingredients = json.loads(meal.ingredients)
                    for ingredient in ingredients:
                        # Check if ingredient is available in stock
                        available = any(
                            item.item_name.lower() in ingredient['name'].lower() or
                            ingredient['name'].lower() in item.item_name.lower()
                            for item in stock_items
                        )
                        
                        if not available:
                            shopping_list.append(
                                f"{ingredient['name']} - {ingredient['quantity']} {ingredient['unit']}"
                            )
                except (json.JSONDecodeError, AttributeError):
                    logger.warning(f"Invalid ingredients format for meal {meal.id}")
                    continue
        
        # Remove duplicates
        return list(set(shopping_list))

    def _load_meal_templates(self) -> List[Dict[str, Any]]:
        """Load meal templates for local testing."""
        return [
            {
                'name': 'Healthy Breakfast Bowl',
                'meal_type': 'breakfast',
                'cuisine': 'international',
                'ingredients': [
                    {'name': 'oats', 'quantity': 50, 'unit': 'g'},
                    {'name': 'milk', 'quantity': 200, 'unit': 'ml'},
                    {'name': 'banana', 'quantity': 1, 'unit': 'pcs'},
                    {'name': 'honey', 'quantity': 10, 'unit': 'g'},
                    {'name': 'nuts', 'quantity': 20, 'unit': 'g'}
                ],
                'cooking_instructions': 'Cook oats with milk, top with sliced banana, honey, and nuts.',
                'calories': 350,
                'protein': 12,
                'carbs': 55,
                'fat': 8
            },
            {
                'name': 'Grilled Chicken Salad',
                'meal_type': 'lunch',
                'cuisine': 'mediterranean',
                'ingredients': [
                    {'name': 'chicken breast', 'quantity': 150, 'unit': 'g'},
                    {'name': 'lettuce', 'quantity': 100, 'unit': 'g'},
                    {'name': 'tomatoes', 'quantity': 100, 'unit': 'g'},
                    {'name': 'olive oil', 'quantity': 15, 'unit': 'ml'},
                    {'name': 'lemon', 'quantity': 1, 'unit': 'pcs'}
                ],
                'cooking_instructions': 'Grill chicken, chop vegetables, mix with olive oil and lemon.',
                'calories': 280,
                'protein': 35,
                'carbs': 8,
                'fat': 12
            },
            {
                'name': 'Vegetarian Pasta',
                'meal_type': 'dinner',
                'cuisine': 'italian',
                'ingredients': [
                    {'name': 'pasta', 'quantity': 100, 'unit': 'g'},
                    {'name': 'tomato sauce', 'quantity': 150, 'unit': 'ml'},
                    {'name': 'vegetables', 'quantity': 150, 'unit': 'g'},
                    {'name': 'cheese', 'quantity': 30, 'unit': 'g'},
                    {'name': 'herbs', 'quantity': 5, 'unit': 'g'}
                ],
                'cooking_instructions': 'Cook pasta, prepare sauce with vegetables, combine and top with cheese.',
                'calories': 420,
                'protein': 15,
                'carbs': 65,
                'fat': 12
            }
        ]

    def _load_nutritional_data(self) -> Dict[str, Any]:
        """Load nutritional data for common ingredients."""
        return {
            'oats': {'calories': 389, 'protein': 16.9, 'carbs': 66.3, 'fat': 6.9},
            'milk': {'calories': 42, 'protein': 3.4, 'carbs': 5.0, 'fat': 1.0},
            'banana': {'calories': 89, 'protein': 1.1, 'carbs': 22.8, 'fat': 0.3},
            'chicken breast': {'calories': 165, 'protein': 31.0, 'carbs': 0.0, 'fat': 3.6},
            'lettuce': {'calories': 15, 'protein': 1.4, 'carbs': 2.9, 'fat': 0.1},
            'pasta': {'calories': 131, 'protein': 5.0, 'carbs': 25.0, 'fat': 1.1}
        }
