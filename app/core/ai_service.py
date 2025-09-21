import logging
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

# AI Service Interface
class AIServiceInterface(ABC):
    """Abstract base class for AI service implementations."""
    
    @abstractmethod
    def generate_meal_suggestions(self, user_preferences: Dict, available_ingredients: List[str]) -> List[Dict]:
        """Generate meal suggestions based on user preferences and available ingredients."""
        pass
    
    @abstractmethod
    def analyze_nutritional_value(self, ingredients: List[str]) -> Dict:
        """Analyze nutritional value of given ingredients."""
        pass
    
    @abstractmethod
    def get_ingredient_substitutes(self, ingredient: str, constraints: Optional[List[str]] = None) -> List[str]:
        """Get possible substitutes for an ingredient."""
        pass


class LocalAIService(AIServiceInterface):
    """Local implementation of AI service using simpler models or rules."""
    
    def generate_meal_suggestions(self, user_preferences: Dict, available_ingredients: List[str]) -> List[Dict]:
        """Generate meal suggestions using local rules/models."""
        # For development/testing
        return [
            {
                "name": "Simple Salad",
                "ingredients": ["lettuce", "tomato", "cucumber"],
                "instructions": "Mix all ingredients together",
                "nutrition": {"calories": 100, "protein": 2, "carbs": 5}
            }
        ]
    
    def analyze_nutritional_value(self, ingredients: List[str]) -> Dict:
        """Analyze nutritional value using local database/rules."""
        return {
            "calories": 200,
            "protein": 10,
            "carbs": 25,
            "fat": 8,
            "vitamins": ["A", "C"]
        }
    
    def get_ingredient_substitutes(self, ingredient: str, constraints: Optional[List[str]] = None) -> List[str]:
        """Get ingredient substitutes using local database/rules."""
        basic_substitutes = {
            "milk": ["almond milk", "soy milk", "oat milk"],
            "egg": ["flax seed", "chia seed", "banana"],
            "flour": ["almond flour", "coconut flour", "oat flour"]
        }
        return basic_substitutes.get(ingredient.lower(), [])


# Global AI service instances
ai_service_client: Optional[Any] = None
weaviate_client: Optional[Any] = None
langchain_llm: Optional[Any] = None


async def init_ai_service():
    """Initialize AI service components"""
    global ai_service_client, weaviate_client, langchain_llm
    
    try:
        logger.info("🤖 Initializing AI services...")
        
        # Initialize Weaviate vector database
        await init_weaviate()
        
        # Initialize LangChain and models
        await init_langchain()
        
        # Initialize AI service client
        await init_ai_client()
        
        logger.info("✅ AI services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ AI service initialization failed: {e}")
        logger.info("🔄 Continuing with mock AI services for local development")


async def init_weaviate():
    """Initialize Weaviate vector database"""
    global weaviate_client
    
    try:
        # For local development, we'll use a mock Weaviate client
        # In production, this would connect to the actual Weaviate instance
        if settings.ENVIRONMENT == "development":
            logger.info("🔄 Using mock Weaviate for local development")
            weaviate_client = MockWeaviateClient()
        else:
            # Production Weaviate connection would go here
            pass
            
    except Exception as e:
        logger.error(f"❌ Weaviate initialization failed: {e}")
        weaviate_client = MockWeaviateClient()


async def init_langchain():
    """Initialize LangChain and language models"""
    global langchain_llm
    
    try:
        if settings.USE_LOCAL_MODELS:
            logger.info("🔄 Using local language models")
            # For local development, we'll use a mock LLM
            # In production, this would load actual Hugging Face models
            langchain_llm = MockLangChainLLM()
        else:
            # Production model loading would go here
            pass
            
    except Exception as e:
        logger.error(f"❌ LangChain initialization failed: {e}")
        langchain_llm = MockLangChainLLM()


async def init_ai_client():
    """Initialize AI service client"""
    global ai_service_client
    
    try:
        # For local development, we'll use a mock AI service
        # In production, this would connect to the actual AI service
        if settings.ENVIRONMENT == "development":
            logger.info("🔄 Using mock AI service for local development")
            ai_service_client = MockAIServiceClient()
        else:
            # Production AI service connection would go here
            pass
            
    except Exception as e:
        logger.error(f"❌ AI service client initialization failed: {e}")
        ai_service_client = MockAIServiceClient()


async def close_ai_service():
    """Close AI service connections"""
    global ai_service_client, weaviate_client, langchain_llm
    
    try:
        if weaviate_client:
            await weaviate_client.close()
        if langchain_llm:
            await langchain_llm.close()
        if ai_service_client:
            await ai_service_client.close()
        logger.info("✅ AI services closed")
    except Exception as e:
        logger.error(f"❌ Failed to close AI services: {e}")


# Mock classes for local development
class MockWeaviateClient:
    """Mock Weaviate client for local development"""
    
    def __init__(self):
        self.collections = {}
        self.vectors = {}
    
    async def create_collection(self, name: str, properties: Dict[str, Any]):
        """Mock collection creation"""
        self.collections[name] = properties
        logger.info(f"📚 Mock collection '{name}' created")
        return {"name": name, "status": "created"}
    
    async def add_data_object(self, collection: str, data: Dict[str, Any], vector: list = None):
        """Mock data object addition"""
        if collection not in self.vectors:
            self.vectors[collection] = []
        
        obj_id = len(self.vectors[collection]) + 1
        self.vectors[collection].append({
            "id": obj_id,
            "data": data,
            "vector": vector or [0.0] * 128
        })
        logger.info(f"📝 Mock data object added to collection '{collection}'")
        return {"id": obj_id}
    
    async def query(self, collection: str, query: str, limit: int = 10):
        """Mock query execution"""
        if collection not in self.vectors:
            return []
        
        # Simple mock search - in production this would use vector similarity
        results = []
        for obj in self.vectors[collection][:limit]:
            if query.lower() in str(obj["data"]).lower():
                results.append(obj)
        
        logger.info(f"🔍 Mock query executed on collection '{collection}'")
        return results
    
    async def close(self):
        """Mock close method"""
        pass


class MockLangChainLLM:
    """Mock LangChain LLM for local development"""
    
    def __init__(self):
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS
    
    async def generate(self, prompt: str, **kwargs):
        """Mock text generation"""
        # Simple mock responses based on prompt content
        if "meal" in prompt.lower():
            response = "Here's a healthy meal suggestion: Grilled chicken with quinoa and steamed vegetables."
        elif "stock" in prompt.lower():
            response = "Based on your stock, I recommend using the rice and vegetables for tonight's meal."
        elif "health" in prompt.lower():
            response = "For better health, consider adding more leafy greens and reducing processed foods."
        else:
            response = "I understand your request. How can I help you with meal planning or food management?"
        
        logger.info(f"🤖 Mock LLM generated response for prompt: {prompt[:50]}...")
        return {
            "generations": [[{"text": response}]],
            "llm_output": {"token_usage": {"total_tokens": len(prompt.split()) + len(response.split())}}
        }
    
    async def close(self):
        """Mock close method"""
        pass


class MockAIServiceClient:
    """Mock AI service client for local development"""
    
    def __init__(self):
        self.meal_templates = {
            "breakfast": ["Oatmeal with fruits", "Eggs with toast", "Smoothie bowl"],
            "lunch": ["Grilled chicken salad", "Vegetable stir-fry", "Lentil soup"],
            "dinner": ["Baked salmon", "Vegetarian pasta", "Chicken curry"]
        }
    
    async def generate_meal_plan(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Mock meal plan generation"""
        diet = user_preferences.get("diet", "vegetarian")
        meal_type = user_preferences.get("meal_type", "dinner")
        
        # Simple mock meal generation
        if diet == "vegetarian":
            if meal_type == "breakfast":
                meal = "Oatmeal with berries and nuts"
            elif meal_type == "lunch":
                meal = "Quinoa salad with vegetables"
            else:
                meal = "Vegetarian pasta with tomato sauce"
        else:
            if meal_type == "breakfast":
                meal = "Eggs with whole grain toast"
            elif meal_type == "lunch":
                meal = "Grilled chicken with rice"
            else:
                meal = "Baked salmon with quinoa"
        
        logger.info(f"🍽️ Mock meal generated: {meal}")
        return {
            "meal": meal,
            "calories": 450,
            "protein": 25,
            "carbs": 45,
            "fat": 15,
            "ingredients": ["ingredient1", "ingredient2", "ingredient3"],
            "cooking_time": "30 minutes"
        }
    
    async def analyze_food_image(self, image_data: bytes) -> Dict[str, Any]:
        """Mock food image analysis"""
        logger.info("📸 Mock food image analysis completed")
        return {
            "item_name": "Rice",
            "category": "grains",
            "weight": 1.0,
            "unit": "kg",
            "calories_per_100g": 130,
            "protein_per_100g": 2.7,
            "carbs_per_100g": 28,
            "fat_per_100g": 0.3,
            "confidence": 0.95
        }
    
    async def get_health_recommendations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Mock health recommendations"""
        age = user_profile.get("age", 30)
        gender = user_profile.get("gender", "other")
        
        recommendations = []
        if age > 50:
            recommendations.append("Consider adding more calcium-rich foods for bone health")
        if gender == "female":
            recommendations.append("Include iron-rich foods like spinach and legumes")
        
        logger.info(f"💊 Mock health recommendations generated for {age} year old {gender}")
        return {
            "recommendations": recommendations,
            "priority": "medium",
            "next_checkup": "3 months"
        }
    
    async def close(self):
        """Mock close method"""
        pass


# Health check
def check_ai_service_health() -> bool:
    """Check if AI services are accessible"""
    try:
        return (
            ai_service_client is not None and
            weaviate_client is not None and
            langchain_llm is not None
        )
    except Exception as e:
        logger.error(f"❌ AI service health check failed: {e}")
        return False

