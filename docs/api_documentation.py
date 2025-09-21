"""
API Documentation generator and endpoint documentation.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app


def generate_api_docs():
    """Generate comprehensive API documentation"""
    
    docs = {
        "title": "Money - Health Food App API",
        "version": "1.0.0",
        "description": "Backend API for comprehensive food management and health tracking",
        "endpoints": {
            "authentication": {
                "POST /api/v1/auth/signup": {
                    "description": "Basic user registration with minimal required fields",
                    "request_body": {
                        "email": "string (required)",
                        "first_name": "string (required)",
                        "last_name": "string (required)", 
                        "address": "string (required)",
                        "password": "string (required, min 8 chars)"
                    },
                    "response": "TokenResponse with user data and access token"
                },
                "POST /api/v1/auth/signin": {
                    "description": "User authentication with email/phone and password",
                    "request_body": {
                        "username": "string (email or phone)",
                        "password": "string"
                    },
                    "response": "TokenResponse with access and refresh tokens"
                },
                "POST /api/v1/auth/complete-profile": {
                    "description": "Complete user profile with detailed information",
                    "headers": {"Authorization": "Bearer <token>"},
                    "request_body": {
                        "phone": "string",
                        "height": "float",
                        "weight": "float",
                        "age": "integer",
                        "gender": "enum (male, female, transgender, other)",
                        "diet": "enum (vegan, vegetarian, eggetarian, non_vegetarian)",
                        "cuisines": "array of strings (min 2, max 6)"
                    }
                },
                "GET /api/v1/auth/profile": {
                    "description": "Get current user profile",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "UserProfileResponse with complete user data"
                }
            },
            "stock_management": {
                "POST /api/v1/stock/": {
                    "description": "Create new stock item",
                    "headers": {"Authorization": "Bearer <token>"},
                    "request_body": {
                        "item_name": "string",
                        "category": "string",
                        "quantity": "float",
                        "unit": "string",
                        "price_per_unit": "float",
                        "purchase_date": "date",
                        "expiry_date": "date (optional)",
                        "supplier": "string (optional)",
                        "minimum_stock_level": "float"
                    }
                },
                "GET /api/v1/stock/": {
                    "description": "List all stock items with filtering",
                    "headers": {"Authorization": "Bearer <token>"},
                    "query_params": {
                        "category": "string (optional)",
                        "expiring_soon": "boolean (optional)",
                        "low_stock": "boolean (optional)"
                    }
                },
                "GET /api/v1/stock/analytics": {
                    "description": "Get stock analytics and insights",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Stock analytics with expiry alerts, low stock warnings"
                }
            },
            "meal_management": {
                "POST /api/v1/meals/": {
                    "description": "Create new meal plan",
                    "headers": {"Authorization": "Bearer <token>"},
                    "request_body": {
                        "name": "string",
                        "meal_type": "enum (breakfast, lunch, dinner, snack)",
                        "ingredients": "array of strings",
                        "instructions": "string",
                        "prep_time": "integer (minutes)",
                        "cook_time": "integer (minutes)",
                        "servings": "integer",
                        "calories_per_serving": "integer (optional)",
                        "scheduled_for": "date"
                    }
                },
                "GET /api/v1/meals/": {
                    "description": "List meals with filtering options",
                    "headers": {"Authorization": "Bearer <token>"},
                    "query_params": {
                        "meal_type": "string (optional)",
                        "date_from": "date (optional)",
                        "date_to": "date (optional)"
                    }
                },
                "POST /api/v1/meals/generate": {
                    "description": "Generate AI-powered meal suggestions",
                    "headers": {"Authorization": "Bearer <token>"},
                    "request_body": {
                        "meal_type": "string",
                        "dietary_preferences": "array of strings",
                        "cuisine_preferences": "array of strings",
                        "target_date": "date",
                        "servings": "integer",
                        "budget_limit": "float (optional)"
                    }
                }
            },
            "user_management": {
                "GET /api/v1/users/": {
                    "description": "List users (admin or family members)",
                    "headers": {"Authorization": "Bearer <token>"},
                    "response": "Array of user profiles"
                },
                "GET /api/v1/users/{id}": {
                    "description": "Get specific user by ID",
                    "headers": {"Authorization": "Bearer <token>"},
                    "path_params": {"id": "integer"},
                    "response": "UserResponse with detailed profile"
                }
            }
        },
        "schemas": {
            "UserSignUpBasic": {
                "email": "EmailStr",
                "password": "str (min 8 chars)",
                "first_name": "str (1-100 chars)",
                "last_name": "str (1-100 chars)",
                "address": "str (min 10 chars)"
            },
            "TokenResponse": {
                "access_token": "str",
                "refresh_token": "str", 
                "token_type": "str",
                "user_id": "int",
                "message": "str"
            },
            "StockCreate": {
                "item_name": "str",
                "category": "str",
                "quantity": "float (>0)",
                "unit": "str",
                "price_per_unit": "float (>0)",
                "purchase_date": "date",
                "expiry_date": "date (optional)",
                "supplier": "str (optional)",
                "minimum_stock_level": "float (>0)"
            },
            "MealCreate": {
                "name": "str",
                "meal_type": "enum",
                "ingredients": "List[str]",
                "instructions": "str",
                "prep_time": "int (>0)",
                "cook_time": "int (>0)",
                "servings": "int (>0)",
                "calories_per_serving": "int (optional)",
                "scheduled_for": "date"
            }
        },
        "authentication": {
            "type": "Bearer Token",
            "description": "Include 'Authorization: Bearer <token>' header for protected endpoints",
            "token_expiry": "30 minutes for access token, 7 days for refresh token"
        },
        "error_responses": {
            "400": "Bad Request - Invalid input data",
            "401": "Unauthorized - Invalid or missing token",
            "403": "Forbidden - Insufficient permissions",
            "404": "Not Found - Resource not found",
            "422": "Validation Error - Request validation failed",
            "500": "Internal Server Error - Server error"
        }
    }
    
    return docs


def print_api_summary():
    """Print API endpoint summary"""
    docs = generate_api_docs()
    
    print("🚀 MONEY - HEALTH FOOD APP API")
    print("=" * 50)
    print(f"Version: {docs['version']}")
    print(f"Description: {docs['description']}")
    
    print(f"\n📋 AVAILABLE ENDPOINTS:")
    print("-" * 30)
    
    for category, endpoints in docs['endpoints'].items():
        print(f"\n🔹 {category.upper().replace('_', ' ')}")
        for endpoint, details in endpoints.items():
            print(f"  {endpoint}")
            print(f"    {details['description']}")
    
    print(f"\n🔐 AUTHENTICATION:")
    print(f"  Type: {docs['authentication']['type']}")
    print(f"  {docs['authentication']['description']}")
    
    print(f"\n📊 SCHEMAS: {len(docs['schemas'])} defined")
    print(f"🚨 ERROR CODES: {len(docs['error_responses'])} handled")
    print("=" * 50)


if __name__ == "__main__":
    print_api_summary()
    
    # Save documentation to file
    import json
    docs = generate_api_docs()
    with open("api_documentation.json", "w") as f:
        json.dump(docs, f, indent=2)
    
    print("💾 Full API documentation saved to api_documentation.json")
