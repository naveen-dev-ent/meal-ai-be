# Money-Health Backend API

A comprehensive backend API for food management, health tracking, and meal planning with enterprise-grade security and monitoring.

## 📁 New Project Structure

```
backend/
├── src/                           # Source code root
│   ├── api/                       # API endpoints
│   │   └── v1/                    # API version 1
│   │       ├── endpoints/         # Route handlers
│   │       └── api.py             # API router configuration
│   │
│   ├── core/                      # Core application logic
│   │   ├── database.py           # Database connection and models
│   │   ├── security.py           # Authentication and authorization
│   │   └── config.py             # Core configuration
│   │
│   ├── middleware/                # Custom middleware
│   │   ├── auth_middleware.py    # Authentication middleware
│   │   ├── monitoring_middleware.py # Request monitoring
│   │   └── security_middleware.py # Security headers and HTTPS
│   │
│   ├── models/                   # Database models
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   └── utils/                    # Helper functions
│
├── config/                       # Configuration files
│   ├── environment.py            # Environment variables
│   ├── logging_config.py         # Logging setup
│   └── ssl_config.py             # SSL configuration
│
├── scripts/                      # Utility scripts
│   ├── database_setup.py         # Database management
│   └── https_server.py           # HTTPS server setup
│
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
│
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Example environment config
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── setup.py                      # Package configuration
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Unix/macOS

# Install package in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Copy example environment file
cp .env.example .env
```

### 2. Configuration

Update `.env` with your configuration:
```ini
# Application
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///./money_health.db
DATABASE_TEST_URL=sqlite:///./test.db

# Security
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

### 3. Database Setup

```bash
# Initialize database
python -m scripts.database_setup --create

# Run migrations
python -m alembic upgrade head
```

### 4. Run the Application

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Production server with HTTPS
python -m scripts.https_server
```

### 3. Start Application
```bash
# Start with environment checks
python scripts/startup.py

# Or start directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Access interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/auth/signin` - User login
- `POST /api/v1/auth/complete-profile` - Complete user profile
- `GET /api/v1/auth/profile` - Get user profile

#### Stock Management
- `POST /api/v1/stock/` - Create stock item
- `GET /api/v1/stock/` - List stock items
- `GET /api/v1/stock/analytics` - Stock analytics

#### Meal Management
- `POST /api/v1/meals/` - Create meal plan
- `GET /api/v1/meals/` - List meals
- `POST /api/v1/meals/generate` - AI meal suggestions

## 🛠️ Development Tools

### Database Management
```bash
# Create tables
python scripts/database_setup.py --create

# Reset database
python scripts/database_setup.py --reset

# Backup database
python migrations/migration_manager.py --backup
```

### Testing
```bash
# Run comprehensive tests
python utils/testing_tools.py

# Generate API documentation
python docs/api_documentation.py
```

### Migration Management
```bash
# Create new migration
python migrations/migration_manager.py --create "migration_name"

# List migrations
python migrations/migration_manager.py --list

# Validate schema
python migrations/migration_manager.py --validate
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
ENVIRONMENT=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./data/app.db
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:19006
```

### Environment-Specific Settings
- **Development**: Debug mode, local database, CORS enabled
- **Testing**: In-memory database, minimal logging
- **Production**: Optimized settings, external database

## 📊 Features

### User Management
- Multi-step registration process
- Profile completion with health metrics
- Family member management
- Address management

### Stock Management
- Inventory tracking with expiry dates
- Low stock alerts
- Purchase history
- Supplier management

### Meal Planning
- AI-powered meal suggestions
- Dietary preference integration
- Nutritional information
- Shopping list generation

### Health Tracking
- Health condition management
- Dietary restrictions
- Nutritional goals
- Progress tracking

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- CORS protection
- Input validation

## 📝 Logging

Logs are stored in the `logs/` directory:
- `app.log` - General application logs
- `errors.log` - Error-specific logs

## 🧪 Testing

The backend includes comprehensive testing utilities:
- Schema validation
- API endpoint testing
- Dummy data generation
- Database testing

## 📦 Dependencies

Key dependencies:
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **Alembic** - Database migrations
- **Uvicorn** - ASGI server
- **python-jose** - JWT handling
- **passlib** - Password hashing

## 🤝 Contributing

1. Follow the established directory structure
2. Add comprehensive tests for new features
3. Update documentation
4. Use proper logging
5. Follow PEP 8 style guidelines

## 📄 License

This project is part of the Money-Health application suite.
