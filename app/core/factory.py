"""
Factory pattern implementation for creating service instances.

This module provides factory classes that create and configure
service instances, promoting loose coupling and dependency injection.
"""

from typing import Dict, Type, Any, Optional
from functools import lru_cache

from app.core.base import (
    ServiceInterface,
    CacheInterface,
    NotificationInterface,
    AIServiceInterface,
)
from app.core.config import settings
from app.services.meal_service import MealService
from app.services.stock_service import StockService
from app.core.cache import CacheManager
from app.core.notifications import EmailNotificationService
from app.core.ai_service import LocalAIService


class ServiceFactory:
    """
    Factory class for creating service instances.
    
    This class implements the Factory pattern to create and configure
    service instances with proper dependencies.
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._cache: Optional[CacheInterface] = None
        self._notification_service: Optional[NotificationInterface] = None
        self._ai_service: Optional[AIServiceInterface] = None

    @property
    def cache(self) -> CacheInterface:
        """Get or create cache service instance."""
        if self._cache is None:
            self._cache = self._create_cache_service()
        return self._cache

    @property
    def notification_service(self) -> NotificationInterface:
        """Get or create notification service instance."""
        if self._notification_service is None:
            self._notification_service = self._create_notification_service()
        return self._notification_service

    @property
    def ai_service(self) -> AIServiceInterface:
        """Get or create AI service instance."""
        if self._ai_service is None:
            self._ai_service = self._create_ai_service()
        return self._ai_service

    def get_service(self, service_name: str) -> Any:
        """
        Get a service instance by name.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service name is not recognized
        """
        if service_name not in self._services:
            self._services[service_name] = self._create_service(service_name)
        return self._services[service_name]

    def _create_service(self, service_name: str) -> Any:
        """
        Create a service instance by name.
        
        Args:
            service_name: Name of the service to create
            
        Returns:
            New service instance
            
        Raises:
            ValueError: If service name is not recognized
        """
        service_creators = {
            "meal": self._create_meal_service,
            "stock": self._create_stock_service,
        }

        if service_name not in service_creators:
            raise ValueError(f"Unknown service: {service_name}")

        return service_creators[service_name]()

    def _create_meal_service(self) -> MealService:
        """Create and configure meal service instance."""
        return MealService(
            cache_service=self.cache,
            ai_service=self.ai_service,
            notification_service=self.notification_service,
        )

    def _create_stock_service(self) -> StockService:
        """Create and configure stock service instance."""
        return StockService(
            cache_service=self.cache,
            notification_service=self.notification_service,
        )

    def _create_cache_service(self) -> CacheInterface:
        """Create cache service instance based on configuration."""
        return CacheManager()

    def _create_notification_service(self) -> NotificationInterface:
        """Create notification service instance based on configuration."""
        if settings.ENABLE_EMAIL_NOTIFICATIONS:
            return EmailNotificationService()
        else:
            from app.core.notifications import MockNotificationService
            return MockNotificationService()

    def _create_ai_service(self) -> AIServiceInterface:
        """Create AI service instance based on configuration."""
        if settings.USE_LOCAL_MODELS:
            return LocalAIService()
        else:
            from app.core.ai_service import CloudAIService
            return CloudAIService()

    def reset(self):
        """Reset all service instances (useful for testing)."""
        self._services.clear()
        self._cache = None
        self._notification_service = None
        self._ai_service = None


class RepositoryFactory:
    """
    Factory class for creating repository instances.
    
    This class implements the Factory pattern to create and configure
    repository instances with proper database connections.
    """

    def __init__(self):
        self._repositories: Dict[str, Any] = {}

    def get_repository(self, repository_name: str) -> Any:
        """
        Get a repository instance by name.
        
        Args:
            repository_name: Name of the repository to retrieve
            
        Returns:
            Repository instance
            
        Raises:
            ValueError: If repository name is not recognized
        """
        if repository_name not in self._repositories:
            self._repositories[repository_name] = self._create_repository(
                repository_name
            )
        return self._repositories[repository_name]

    def _create_repository(self, repository_name: str) -> Any:
        """
        Create a repository instance by name.
        
        Args:
            repository_name: Name of the repository to create
            
        Returns:
            New repository instance
            
        Raises:
            ValueError: If repository name is not recognized
        """
        # This would be implemented when repositories are created
        raise NotImplementedError(f"Repository {repository_name} not implemented yet")

    def reset(self):
        """Reset all repository instances (useful for testing)."""
        self._repositories.clear()


# Global factory instances
@lru_cache()
def get_service_factory() -> ServiceFactory:
    """Get the global service factory instance."""
    return ServiceFactory()


@lru_cache()
def get_repository_factory() -> RepositoryFactory:
    """Get the global repository factory instance."""
    return RepositoryFactory()


class DependencyContainer:
    """
    Dependency injection container for managing service dependencies.
    
    This class provides a centralized way to manage and inject
    dependencies throughout the application.
    """

    def __init__(self):
        self.service_factory = get_service_factory()
        self.repository_factory = get_repository_factory()

    def get_meal_service(self) -> MealService:
        """Get meal service with dependencies."""
        return self.service_factory.get_service("meal")

    def get_stock_service(self) -> StockService:
        """Get stock service with dependencies."""
        return self.service_factory.get_service("stock")

    def get_cache_service(self) -> CacheInterface:
        """Get cache service."""
        return self.service_factory.cache

    def get_notification_service(self) -> NotificationInterface:
        """Get notification service."""
        return self.service_factory.notification_service

    def get_ai_service(self) -> AIServiceInterface:
        """Get AI service."""
        return self.service_factory.ai_service

    def reset(self):
        """Reset all dependencies (useful for testing)."""
        self.service_factory.reset()
        self.repository_factory.reset()


# Global dependency container
@lru_cache()
def get_dependency_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    return DependencyContainer()
