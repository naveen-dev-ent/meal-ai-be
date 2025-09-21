"""
External services configuration and monitoring setup.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AlertChannel(Enum):
    """Alert notification channels"""
    LOG = "log"
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"

@dataclass
class ServiceConfig:
    """External service configuration"""
    name: str
    health_url: str
    timeout_seconds: float = 10.0
    retry_attempts: int = 3
    alert_channels: List[AlertChannel] = None
    critical: bool = False
    
    def __post_init__(self):
        if self.alert_channels is None:
            self.alert_channels = [AlertChannel.LOG]

class ExternalServicesConfig:
    """Configuration for external services monitoring"""
    
    def __init__(self):
        self.services = self._load_services_config()
        self.alert_thresholds = self._load_alert_thresholds()
        self.notification_config = self._load_notification_config()
    
    def _load_services_config(self) -> Dict[str, ServiceConfig]:
        """Load external services configuration"""
        services = {}
        
        # Payment services
        if os.getenv("STRIPE_API_KEY"):
            services["stripe"] = ServiceConfig(
                name="Stripe Payment Service",
                health_url="https://status.stripe.com/api/v2/status.json",
                timeout_seconds=15.0,
                critical=True,
                alert_channels=[AlertChannel.LOG, AlertChannel.EMAIL]
            )
        
        # Email services
        if os.getenv("SENDGRID_API_KEY"):
            services["sendgrid"] = ServiceConfig(
                name="SendGrid Email Service",
                health_url="https://status.sendgrid.com/api/v2/status.json",
                timeout_seconds=10.0,
                critical=True,
                alert_channels=[AlertChannel.LOG]
            )
        
        # Cloud storage
        if os.getenv("CLOUDINARY_URL"):
            services["cloudinary"] = ServiceConfig(
                name="Cloudinary Storage Service",
                health_url="https://status.cloudinary.com/api/v2/status.json",
                timeout_seconds=10.0,
                critical=False,
                alert_channels=[AlertChannel.LOG]
            )
        
        # External APIs
        if os.getenv("NUTRITION_API_KEY"):
            services["nutrition_api"] = ServiceConfig(
                name="Nutrition Data API",
                health_url=f"{os.getenv('NUTRITION_API_BASE_URL', 'https://api.nutritionix.com')}/v1_1/search",
                timeout_seconds=20.0,
                critical=False,
                alert_channels=[AlertChannel.LOG]
            )
        
        # Redis cache (if configured)
        if os.getenv("REDIS_URL"):
            services["redis"] = ServiceConfig(
                name="Redis Cache Service",
                health_url=f"{os.getenv('REDIS_URL')}/ping",
                timeout_seconds=5.0,
                critical=False,
                alert_channels=[AlertChannel.LOG]
            )
        
        return services
    
    def _load_alert_thresholds(self) -> Dict[str, float]:
        """Load alerting thresholds"""
        return {
            "cpu_threshold": float(os.getenv("CPU_ALERT_THRESHOLD", "80.0")),
            "memory_threshold": float(os.getenv("MEMORY_ALERT_THRESHOLD", "85.0")),
            "disk_threshold": float(os.getenv("DISK_ALERT_THRESHOLD", "90.0")),
            "response_time_threshold": float(os.getenv("RESPONSE_TIME_THRESHOLD", "3.0")),
            "error_rate_threshold": float(os.getenv("ERROR_RATE_THRESHOLD", "5.0")),
            "consecutive_failures_threshold": int(os.getenv("CONSECUTIVE_FAILURES_THRESHOLD", "3"))
        }
    
    def _load_notification_config(self) -> Dict[str, str]:
        """Load notification configuration"""
        return {
            "email_recipients": os.getenv("ALERT_EMAIL_RECIPIENTS", ""),
            "slack_webhook": os.getenv("SLACK_WEBHOOK_URL", ""),
            "webhook_url": os.getenv("ALERT_WEBHOOK_URL", ""),
            "email_smtp_server": os.getenv("SMTP_SERVER", ""),
            "email_smtp_port": os.getenv("SMTP_PORT", "587"),
            "email_username": os.getenv("SMTP_USERNAME", ""),
            "email_password": os.getenv("SMTP_PASSWORD", "")
        }
    
    def get_critical_services(self) -> List[ServiceConfig]:
        """Get list of critical external services"""
        return [service for service in self.services.values() if service.critical]
    
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """Get configuration for a specific service"""
        return self.services.get(service_name)
    
    def get_all_services(self) -> Dict[str, ServiceConfig]:
        """Get all configured external services"""
        return self.services
    
    def should_alert(self, metric_name: str, value: float) -> bool:
        """Check if a metric value should trigger an alert"""
        threshold = self.alert_thresholds.get(metric_name)
        if threshold is None:
            return False
        
        if metric_name == "consecutive_failures_threshold":
            return int(value) >= int(threshold)
        
        return value >= threshold

# Global configuration instance
external_services_config = ExternalServicesConfig()
