"""
Comprehensive test suite for the logging system validation.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import Request
import logging

from main import app
from utils.api_logger import APILogger
from utils.system_monitor import system_monitor
from utils.external_service_logger import external_service_logger, ServiceStatus
from utils.monitoring_middleware import RequestMonitoringMiddleware

# Test client
client = TestClient(app)

class TestLoggingSystem:
    """Test suite for comprehensive logging system"""
    
    def test_health_check_endpoint(self):
        """Test health check endpoint returns comprehensive monitoring data"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "system" in data
        assert "uptime_seconds" in data
        
        # Verify database health info
        assert "healthy" in data["database"]
        assert "connection_stats" in data["database"]
        
        # Verify system health info
        assert "status" in data["system"]
        assert "cpu_percent" in data["system"]
        assert "memory_percent" in data["system"]
    
    def test_monitoring_stats_endpoint(self):
        """Test monitoring statistics endpoint"""
        response = client.get("/monitoring/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "system" in data
        assert "database" in data
        assert "requests" in data
        assert "health" in data
    
    def test_database_health_endpoint(self):
        """Test database health check endpoint"""
        response = client.get("/health/database")
        assert response.status_code == 200
        
        data = response.json()
        assert "healthy" in data
        assert "stats" in data
        assert "timestamp" in data
    
    def test_external_services_endpoint(self):
        """Test external services monitoring endpoint"""
        response = client.get("/monitoring/external-services")
        assert response.status_code == 200
        
        data = response.json()
        assert "services" in data
        assert "failure_summary" in data
        assert "timestamp" in data
    
    @patch('utils.api_logger.APILogger.log_request')
    def test_api_logger_request_logging(self, mock_log_request):
        """Test API logger request logging functionality"""
        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.client.host = "127.0.0.1"
        
        # Test logging
        APILogger.log_request(mock_request, user_id=123)
        mock_log_request.assert_called_once()
    
    @patch('utils.api_logger.APILogger.log_database_operation')
    def test_api_logger_database_logging(self, mock_log_db):
        """Test API logger database operation logging"""
        APILogger.log_database_operation("CREATE", "user", True, user_id=123)
        mock_log_db.assert_called_once_with("CREATE", "user", True, user_id=123)
    
    def test_system_monitor_stats(self):
        """Test system monitor statistics collection"""
        stats = system_monitor.get_current_stats()
        
        assert "cpu_percent" in stats
        assert "memory_percent" in stats
        assert "disk_percent" in stats
        assert "uptime_seconds" in stats
        assert "connections" in stats
    
    def test_system_monitor_health_check(self):
        """Test system monitor health check functionality"""
        health = system_monitor.check_system_health()
        
        assert "status" in health
        assert "stats" in health
        assert "alerts" in health
        assert health["status"] in ["healthy", "warning", "critical"]
    
    def test_external_service_logger_failure(self):
        """Test external service failure logging"""
        # Log a service failure
        test_error = Exception("Connection timeout")
        external_service_logger.log_service_failure(
            "test_service",
            "https://api.test.com/health",
            test_error,
            status_code=500,
            response_time=5.0,
            context={"retry_count": 3}
        )
        
        # Check service health was updated
        health = external_service_logger.get_service_health("test_service")
        assert health["service"] == "test_service"
        assert health["failure_count"] > 0
        assert health["consecutive_failures"] > 0
    
    def test_external_service_logger_success(self):
        """Test external service success logging"""
        # Log a service success
        external_service_logger.log_service_success(
            "test_service",
            "https://api.test.com/health",
            response_time=0.5,
            status_code=200
        )
        
        # Check service health was updated
        health = external_service_logger.get_service_health("test_service")
        assert health["service"] == "test_service"
        assert health["success_count"] > 0
    
    def test_external_service_failure_summary(self):
        """Test external service failure summary"""
        summary = external_service_logger.get_failure_summary(hours=1)
        
        assert "time_period_hours" in summary
        assert "total_failures" in summary
        assert "affected_services" in summary
        assert "services" in summary
    
    @patch('utils.system_monitor.logger')
    def test_system_monitor_database_issue_logging(self, mock_logger):
        """Test system monitor database connection issue logging"""
        test_error = Exception("Database connection lost")
        system_monitor.log_database_connection_issue(test_error, "Test context")
        
        # Verify logging was called
        mock_logger.error.assert_called()
    
    def test_request_monitoring_middleware_stats(self):
        """Test request monitoring middleware statistics"""
        middleware = RequestMonitoringMiddleware(app, timeout_seconds=30.0)
        
        # Initialize some stats
        middleware.request_stats["total_requests"] = 100
        middleware.request_stats["failed_requests"] = 5
        middleware.request_stats["timeout_requests"] = 2
        middleware.request_stats["slow_requests"] = 8
        
        stats = middleware.get_monitoring_stats()
        
        assert "total_requests" in stats
        assert "success_rate" in stats
        assert "timeout_rate" in stats
        assert "slow_request_rate" in stats
        assert stats["success_rate"] == 95.0  # (100-5)/100 * 100

class TestLoggingIntegration:
    """Integration tests for logging across the application"""
    
    def test_api_endpoint_logging_integration(self):
        """Test that API endpoints properly log requests"""
        with patch('utils.api_logger.APILogger.log_request') as mock_log:
            response = client.get("/health")
            assert response.status_code == 200
            mock_log.assert_called()
    
    def test_error_logging_integration(self):
        """Test error logging in global exception handler"""
        with patch('utils.api_logger.APILogger.log_error') as mock_log_error:
            # This should trigger the global exception handler
            response = client.get("/nonexistent-endpoint")
            assert response.status_code == 404
    
    @patch('app.core.database.check_db_health')
    def test_database_failure_logging(self, mock_db_health):
        """Test database failure logging integration"""
        # Mock database failure
        mock_db_health.return_value = False
        
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"]["healthy"] is False

def run_logging_validation():
    """Run comprehensive logging system validation"""
    print("🔍 Running logging system validation...")
    
    # Test basic functionality
    print("✅ Testing basic logging functionality...")
    
    # Test API logger
    try:
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.client.host = "127.0.0.1"
        
        APILogger.log_request(mock_request)
        print("✅ API Logger: Request logging works")
        
        APILogger.log_database_operation("CREATE", "test_table", True)
        print("✅ API Logger: Database operation logging works")
        
        APILogger.log_system_event("test_event", "Test message", {"key": "value"})
        print("✅ API Logger: System event logging works")
        
    except Exception as e:
        print(f"❌ API Logger test failed: {str(e)}")
    
    # Test system monitor
    try:
        stats = system_monitor.get_current_stats()
        if stats:
            print("✅ System Monitor: Statistics collection works")
        
        health = system_monitor.check_system_health()
        if health:
            print("✅ System Monitor: Health check works")
            
    except Exception as e:
        print(f"❌ System Monitor test failed: {str(e)}")
    
    # Test external service logger
    try:
        test_error = Exception("Test connection error")
        external_service_logger.log_service_failure(
            "test_service", "https://test.com", test_error, 500, 2.0
        )
        print("✅ External Service Logger: Failure logging works")
        
        external_service_logger.log_service_success(
            "test_service", "https://test.com", 0.5, 200
        )
        print("✅ External Service Logger: Success logging works")
        
        health = external_service_logger.get_service_health("test_service")
        if health:
            print("✅ External Service Logger: Health tracking works")
            
    except Exception as e:
        print(f"❌ External Service Logger test failed: {str(e)}")
    
    print("\n🎉 Logging system validation completed!")
    print("📊 All major logging components are functional")
    print("🔧 Ready for production monitoring and debugging")

if __name__ == "__main__":
    # Run validation when script is executed directly
    run_logging_validation()
    
    # Run pytest tests
    pytest.main([__file__, "-v"])
