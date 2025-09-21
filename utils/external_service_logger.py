"""
External service failure logging and monitoring utility.
"""

import logging
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import json
from utils.api_logger import APILogger

logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """External service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class ServiceFailure:
    """External service failure record"""
    service_name: str
    endpoint: str
    error_type: str
    error_message: str
    status_code: Optional[int]
    response_time: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ServiceHealth:
    """External service health tracking"""
    service_name: str
    status: ServiceStatus
    last_check: datetime
    failure_count: int = 0
    success_count: int = 0
    avg_response_time: float = 0.0
    last_failure: Optional[ServiceFailure] = None
    consecutive_failures: int = 0

class ExternalServiceLogger:
    """Logger for external service failures and health monitoring"""
    
    def __init__(self):
        self.service_health: Dict[str, ServiceHealth] = {}
        self.failure_history: List[ServiceFailure] = []
        self.max_history_size = 1000
        self.health_check_interval = 300  # 5 minutes
        self.failure_threshold = 3  # consecutive failures before marking unhealthy
        
    def log_service_failure(
        self,
        service_name: str,
        endpoint: str,
        error: Exception,
        status_code: Optional[int] = None,
        response_time: float = 0.0,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log external service failure with detailed information"""
        try:
            failure = ServiceFailure(
                service_name=service_name,
                endpoint=endpoint,
                error_type=type(error).__name__,
                error_message=str(error),
                status_code=status_code,
                response_time=response_time,
                timestamp=datetime.utcnow(),
                context=context or {}
            )
            
            # Add to failure history
            self.failure_history.append(failure)
            if len(self.failure_history) > self.max_history_size:
                self.failure_history.pop(0)
            
            # Update service health
            self._update_service_health(service_name, failure, success=False)
            
            # Log the failure
            logger.error(
                f"🔌 EXTERNAL SERVICE FAILURE | {service_name} | "
                f"{endpoint} | {failure.error_type}: {failure.error_message} | "
                f"Status: {status_code} | Response Time: {response_time:.3f}s"
            )
            
            # Log to API logger for centralized tracking
            APILogger.log_system_event(
                "external_service_failure",
                f"{service_name} service failure",
                {
                    "service": service_name,
                    "endpoint": endpoint,
                    "error_type": failure.error_type,
                    "error_message": failure.error_message,
                    "status_code": status_code,
                    "response_time": response_time,
                    "context": context
                }
            )
            
            # Check if service should be marked as unhealthy
            service_health = self.service_health.get(service_name)
            if service_health and service_health.consecutive_failures >= self.failure_threshold:
                self._log_service_unhealthy(service_name, service_health)
                
        except Exception as e:
            logger.error(f"❌ Failed to log service failure: {str(e)}")
    
    def log_service_success(
        self,
        service_name: str,
        endpoint: str,
        response_time: float,
        status_code: int = 200,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log successful external service call"""
        try:
            # Update service health
            self._update_service_health(service_name, None, success=True, response_time=response_time)
            
            # Log success (debug level to avoid spam)
            logger.debug(
                f"✅ EXTERNAL SERVICE SUCCESS | {service_name} | "
                f"{endpoint} | Status: {status_code} | Response Time: {response_time:.3f}s"
            )
            
            # Check if service recovered from unhealthy state
            service_health = self.service_health.get(service_name)
            if service_health and service_health.status == ServiceStatus.UNHEALTHY:
                if service_health.consecutive_failures == 0:
                    self._log_service_recovered(service_name, service_health)
                    
        except Exception as e:
            logger.error(f"❌ Failed to log service success: {str(e)}")
    
    def _update_service_health(
        self,
        service_name: str,
        failure: Optional[ServiceFailure],
        success: bool,
        response_time: float = 0.0
    ):
        """Update service health tracking"""
        try:
            if service_name not in self.service_health:
                self.service_health[service_name] = ServiceHealth(
                    service_name=service_name,
                    status=ServiceStatus.UNKNOWN,
                    last_check=datetime.utcnow()
                )
            
            health = self.service_health[service_name]
            health.last_check = datetime.utcnow()
            
            if success:
                health.success_count += 1
                health.consecutive_failures = 0
                
                # Update average response time
                total_calls = health.success_count + health.failure_count
                if total_calls > 1:
                    health.avg_response_time = (
                        (health.avg_response_time * (total_calls - 1) + response_time) / total_calls
                    )
                else:
                    health.avg_response_time = response_time
                
                # Update status based on performance
                if response_time > 5.0:  # Slow response
                    health.status = ServiceStatus.DEGRADED
                else:
                    health.status = ServiceStatus.HEALTHY
                    
            else:
                health.failure_count += 1
                health.consecutive_failures += 1
                health.last_failure = failure
                
                # Update status based on failure count
                if health.consecutive_failures >= self.failure_threshold:
                    health.status = ServiceStatus.UNHEALTHY
                elif health.consecutive_failures > 1:
                    health.status = ServiceStatus.DEGRADED
                    
        except Exception as e:
            logger.error(f"❌ Failed to update service health: {str(e)}")
    
    def _log_service_unhealthy(self, service_name: str, health: ServiceHealth):
        """Log when a service becomes unhealthy"""
        logger.error(
            f"🚨 SERVICE UNHEALTHY | {service_name} | "
            f"Consecutive failures: {health.consecutive_failures} | "
            f"Last error: {health.last_failure.error_message if health.last_failure else 'Unknown'}"
        )
        
        APILogger.log_system_event(
            "service_unhealthy",
            f"{service_name} marked as unhealthy",
            {
                "service": service_name,
                "consecutive_failures": health.consecutive_failures,
                "failure_count": health.failure_count,
                "success_count": health.success_count,
                "last_error": health.last_failure.error_message if health.last_failure else None
            }
        )
    
    def _log_service_recovered(self, service_name: str, health: ServiceHealth):
        """Log when a service recovers from unhealthy state"""
        logger.info(
            f"🔄 SERVICE RECOVERED | {service_name} | "
            f"Back to healthy status | Success rate improved"
        )
        
        APILogger.log_system_event(
            "service_recovered",
            f"{service_name} recovered to healthy status",
            {
                "service": service_name,
                "total_failures": health.failure_count,
                "total_successes": health.success_count,
                "avg_response_time": health.avg_response_time
            }
        )
    
    def get_service_health(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get health status for specific service or all services"""
        try:
            if service_name:
                health = self.service_health.get(service_name)
                if not health:
                    return {"error": f"Service {service_name} not found"}
                
                return {
                    "service": health.service_name,
                    "status": health.status.value,
                    "last_check": health.last_check.isoformat(),
                    "failure_count": health.failure_count,
                    "success_count": health.success_count,
                    "consecutive_failures": health.consecutive_failures,
                    "avg_response_time": health.avg_response_time,
                    "last_failure": {
                        "error_type": health.last_failure.error_type,
                        "error_message": health.last_failure.error_message,
                        "timestamp": health.last_failure.timestamp.isoformat()
                    } if health.last_failure else None
                }
            else:
                return {
                    service: {
                        "status": health.status.value,
                        "last_check": health.last_check.isoformat(),
                        "failure_count": health.failure_count,
                        "success_count": health.success_count,
                        "consecutive_failures": health.consecutive_failures,
                        "avg_response_time": health.avg_response_time
                    }
                    for service, health in self.service_health.items()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get service health: {str(e)}")
            return {"error": str(e)}
    
    def get_failure_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get failure summary for the last N hours"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_failures = [
                f for f in self.failure_history 
                if f.timestamp >= cutoff_time
            ]
            
            # Group failures by service
            service_failures = {}
            for failure in recent_failures:
                if failure.service_name not in service_failures:
                    service_failures[failure.service_name] = []
                service_failures[failure.service_name].append(failure)
            
            # Calculate summary statistics
            summary = {
                "time_period_hours": hours,
                "total_failures": len(recent_failures),
                "affected_services": len(service_failures),
                "services": {}
            }
            
            for service, failures in service_failures.items():
                error_types = {}
                for failure in failures:
                    error_types[failure.error_type] = error_types.get(failure.error_type, 0) + 1
                
                summary["services"][service] = {
                    "failure_count": len(failures),
                    "error_types": error_types,
                    "avg_response_time": sum(f.response_time for f in failures) / len(failures),
                    "latest_failure": failures[-1].timestamp.isoformat() if failures else None
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Failed to get failure summary: {str(e)}")
            return {"error": str(e)}
    
    async def health_check_external_services(self, services: Dict[str, str]):
        """Perform health checks on external services"""
        try:
            logger.info(f"🔍 Starting health check for {len(services)} external services")
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                for service_name, health_url in services.items():
                    try:
                        start_time = time.time()
                        
                        async with session.get(health_url) as response:
                            response_time = time.time() - start_time
                            
                            if response.status == 200:
                                self.log_service_success(
                                    service_name, health_url, response_time, response.status
                                )
                            else:
                                self.log_service_failure(
                                    service_name, health_url,
                                    Exception(f"Health check failed with status {response.status}"),
                                    response.status, response_time
                                )
                                
                    except Exception as e:
                        response_time = time.time() - start_time
                        self.log_service_failure(
                            service_name, health_url, e, None, response_time
                        )
            
            logger.info("✅ External service health check completed")
            
        except Exception as e:
            logger.error(f"❌ Failed to perform external service health check: {str(e)}")

# Global external service logger instance
external_service_logger = ExternalServiceLogger()
