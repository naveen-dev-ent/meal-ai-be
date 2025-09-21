"""
Base classes and interfaces for the application.

This module provides abstract base classes and interfaces that define
the contract for various components in the system, promoting loose coupling
and adherence to SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from sqlalchemy.orm import Session
from pydantic import BaseModel

# Type variables for generic classes
T = TypeVar("T")
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)
ResponseT = TypeVar("ResponseT", bound=BaseModel)


class ServiceInterface(ABC, Generic[T, CreateT, UpdateT, ResponseT]):
    """
    Abstract base class for all service classes.
    
    This interface defines the contract that all service classes must implement,
    ensuring consistency across the application and promoting testability.
    """

    @abstractmethod
    async def create(
        self, obj_in: CreateT, db: Session, **kwargs
    ) -> ResponseT:
        """Create a new object."""
        pass

    @abstractmethod
    async def get(self, id: int, db: Session) -> Optional[ResponseT]:
        """Get an object by ID."""
        pass

    @abstractmethod
    async def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[ResponseT]:
        """Get multiple objects with pagination."""
        pass

    @abstractmethod
    async def update(
        self, id: int, obj_in: UpdateT, db: Session, **kwargs
    ) -> Optional[ResponseT]:
        """Update an existing object."""
        pass

    @abstractmethod
    async def delete(self, id: int, db: Session) -> bool:
        """Delete an object by ID."""
        pass


class RepositoryInterface(ABC, Generic[T]):
    """
    Abstract base class for repository pattern implementation.
    
    This interface defines the contract for data access operations,
    promoting separation of concerns and testability.
    """

    @abstractmethod
    async def create(self, obj_in: Any, db: Session) -> T:
        """Create a new record."""
        pass

    @abstractmethod
    async def get(self, id: int, db: Session) -> Optional[T]:
        """Get a record by ID."""
        pass

    @abstractmethod
    async def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[T]:
        """Get multiple records with pagination."""
        pass

    @abstractmethod
    async def update(self, id: int, obj_in: Any, db: Session) -> Optional[T]:
        """Update an existing record."""
        pass

    @abstractmethod
    async def delete(self, id: int, db: Session) -> bool:
        """Delete a record by ID."""
        pass


class CacheInterface(ABC):
    """
    Abstract base class for cache operations.
    
    This interface defines the contract for caching operations,
    allowing for different cache implementations (Redis, in-memory, etc.).
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value in cache with optional expiration."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        pass

    @abstractmethod
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key."""
        pass


class NotificationInterface(ABC):
    """
    Abstract base class for notification operations.
    
    This interface defines the contract for sending notifications,
    supporting different channels (email, SMS, push, etc.).
    """

    @abstractmethod
    async def send(
        self, recipient: str, message: str, notification_type: str, **kwargs
    ) -> bool:
        """Send a notification."""
        pass

    @abstractmethod
    async def send_bulk(
        self, recipients: List[str], message: str, notification_type: str, **kwargs
    ) -> Dict[str, bool]:
        """Send notifications to multiple recipients."""
        pass


class AIServiceInterface(ABC):
    """
    Abstract base class for AI service operations.
    
    This interface defines the contract for AI-powered features,
    allowing for different AI implementations (local, cloud, etc.).
    """

    @abstractmethod
    async def generate_meal_plan(
        self, user_preferences: Dict[str, Any], stock_data: List[Any]
    ) -> Dict[str, Any]:
        """Generate a meal plan using AI."""
        pass

    @abstractmethod
    async def analyze_nutrition(
        self, ingredients: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze nutritional content of ingredients."""
        pass

    @abstractmethod
    async def process_image(self, image_data: bytes) -> Dict[str, Any]:
        """Process images for ingredient recognition."""
        pass


class BaseEntity:
    """
    Base class for all database entities.
    
    This class provides common fields and methods that all
    database models should have.
    """

    def __repr__(self) -> str:
        """String representation of the entity."""
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', 'N/A')})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result


class Priority(Enum):
    """Priority levels for various operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Status(Enum):
    """Status values for various entities."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Result:
    """
    Generic result wrapper for service operations.
    
    This class provides a consistent way to return results from
    service methods, including success/failure status and data.
    """

    def __init__(
        self,
        success: bool,
        data: Optional[Any] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.data = data
        self.message = message
        self.error = error
        self.timestamp = datetime.utcnow()

    @classmethod
    def success_result(
        cls, data: Any = None, message: Optional[str] = None
    ) -> "Result":
        """Create a successful result."""
        return cls(success=True, data=data, message=message)

    @classmethod
    def failure_result(
        cls, error: str, message: Optional[str] = None
    ) -> "Result":
        """Create a failure result."""
        return cls(success=False, error=error, message=message)

    def __bool__(self) -> bool:
        """Return success status as boolean."""
        return self.success

    def __repr__(self) -> str:
        """String representation of the result."""
        status = "SUCCESS" if self.success else "FAILURE"
        return f"<Result({status}, data={self.data}, error={self.error})>"
