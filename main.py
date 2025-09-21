from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import asyncio

from app.api.v1.api import api_router
from app.core.database import init_db, close_db, check_db_health, get_connection_stats
from app.utils.api_logger import APILogger, log_system_event
from app.utils.system_monitor import system_monitor
from app.utils.external_service_logger import external_service_logger
from app.config.environment import env_config
from config.logging_config import logger
from config.ssl_config import ssl_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    system_monitor.log_server_startup()
    system_monitor.setup_signal_handlers()
    
    try:
        # Initialize database
        await init_db()
        log_system_event("Database Initialized", "Database connection established")
        logger.info("Database initialized successfully!")
        
        # Start system monitoring
        asyncio.create_task(system_monitor.start_monitoring())
        
        # Log startup completion
        log_system_event("Application Ready", "All services initialized")
        logger.info("All services initialized successfully!")
        
    except Exception as e:
        system_monitor.log_database_connection_issue(e, "During application startup")
        log_system_event("Startup Error", f"Failed to initialize: {str(e)}")
        logger.error(f"Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    system_monitor.stop_monitoring()
    system_monitor.log_server_shutdown()
    
    try:
        await close_db()
        log_system_event("Application Shutdown", "Services shut down successfully")
        logger.info("Services shut down successfully!")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="Money - Health Food App",
    description="A comprehensive food management platform for personalized meal planning and health tracking",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
cors_config = env_config.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/health")
async def health_check(request: Request):
    APILogger.log_request(request)
    log_system_event("Health Check", "System health requested")
    
    # Get comprehensive health information
    db_healthy = check_db_health()
    system_health = system_monitor.check_system_health()
    db_stats = get_connection_stats()
    
    # Determine overall status
    overall_status = "healthy"
    if not db_healthy:
        overall_status = "unhealthy"
    elif system_health.get("status") == "warning":
        overall_status = "warning"
    
    return {
        "status": overall_status,
        "service": "Money - Health Food App",
        "version": "1.0.0",
        "environment": env_config.ENVIRONMENT,
        "timestamp": system_monitor.start_time.isoformat(),
        "uptime_seconds": system_health.get("stats", {}).get("uptime_seconds", 0),
        "database": {
            "healthy": db_healthy,
            "connection_stats": db_stats
        },
        "system": {
            "status": system_health.get("status", "unknown"),
            "alerts": system_health.get("alerts", []),
            "cpu_percent": system_health.get("stats", {}).get("cpu_percent"),
            "memory_percent": system_health.get("stats", {}).get("memory_percent"),
            "disk_percent": system_health.get("stats", {}).get("disk_percent")
        }
    }

# Root endpoint
@app.get("/")
async def root(request: Request):
    APILogger.log_request(request)
    
    return {
        "message": "Welcome to Money - Health Food App",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0",
        "environment": env_config.ENVIRONMENT
    }

# Global exception handler with logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    client_ip = request.client.host if request.client else "Unknown"
    
    # Log the exception
    logger.error(
        f"GLOBAL EXCEPTION | {request.method} {request.url.path} | "
        f"IP: {client_ip} | Error: {type(exc).__name__} - {str(exc)}"
    )
    
    log_system_event(
        "Global Exception", 
        f"{request.method} {request.url.path} - {type(exc).__name__}: {str(exc)}"
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc),
            "path": str(request.url.path),
            "method": request.method
        }
    )

if __name__ == "__main__":
    # Start HTTP server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )