from typing import List, Optional
from abc import ABC, abstractmethod


class NotificationInterface(ABC):
    """Abstract base class for notification services."""

    @abstractmethod
    def send_notification(self, user_id: int, message: str, data: Optional[dict] = None) -> bool:
        """Send a notification to a user."""
        pass

    @abstractmethod
    def send_bulk_notifications(self, user_ids: List[int], message: str, data: Optional[dict] = None) -> List[bool]:
        """Send notifications to multiple users."""
        pass


class MockNotificationService(NotificationInterface):
    """Mock notification service for development and testing."""

    def send_notification(self, user_id: int, message: str, data: Optional[dict] = None) -> bool:
        """Mock sending a notification to a user."""
        print(f"[MOCK] Notification sent to user {user_id}: {message}")
        if data:
            print(f"[MOCK] Additional data: {data}")
        return True

    def send_bulk_notifications(self, user_ids: List[int], message: str, data: Optional[dict] = None) -> List[bool]:
        """Mock sending notifications to multiple users."""
        results = []
        for user_id in user_ids:
            result = self.send_notification(user_id, message, data)
            results.append(result)
        return results


class EmailNotificationService(NotificationInterface):
    """Email-based notification service."""

    def send_notification(self, user_id: int, message: str, data: Optional[dict] = None) -> bool:
        """Send an email notification to a user."""
        # TODO: Implement actual email sending logic here
        print(f"[EMAIL] Notification to user {user_id}: {message}")
        return True

    def send_bulk_notifications(self, user_ids: List[int], message: str, data: Optional[dict] = None) -> List[bool]:
        """Send email notifications to multiple users."""
        results = []
        for user_id in user_ids:
            result = self.send_notification(user_id, message, data)
            results.append(result)
        return results
