"""
System monitoring and logging utilities for server health and performance tracking.
"""

import psutil
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional
import os
import signal
import sys
from utils.api_logger import APILogger

logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring and logging for server health and performance"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.process = psutil.Process()
        self.monitoring_active = False
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time": 5.0
        }
    
    def log_server_startup(self):
        """Log comprehensive server startup information"""
        try:
            system_info = self.get_system_info()
            
            logger.info("🚀 SERVER STARTUP INITIATED")
            logger.info(f"📊 System Info: {system_info['os']} | CPU: {system_info['cpu_count']} cores | RAM: {system_info['total_memory']:.1f}GB")
            logger.info(f"🐍 Python: {system_info['python_version']} | PID: {system_info['process_id']}")
            logger.info(f"📁 Working Directory: {system_info['working_directory']}")
            logger.info(f"🌐 Server Host: {system_info.get('host', 'localhost')} | Port: {system_info.get('port', '8000')}")
            
            APILogger.log_system_event("server_startup", f"Server started with PID {system_info['process_id']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log server startup info: {str(e)}")
    
    def log_server_shutdown(self, signal_received: Optional[str] = None):
        """Log server shutdown information"""
        try:
            uptime = datetime.utcnow() - self.start_time
            final_stats = self.get_current_stats()
            
            logger.info("🛑 SERVER SHUTDOWN INITIATED")
            if signal_received:
                logger.info(f"📡 Signal Received: {signal_received}")
            
            logger.info(f"⏱️ Total Uptime: {uptime}")
            logger.info(f"📊 Final Stats - CPU: {final_stats['cpu_percent']:.1f}% | Memory: {final_stats['memory_percent']:.1f}%")
            logger.info(f"🔗 Database Connections: {final_stats.get('db_connections', 'N/A')}")
            
            APILogger.log_system_event("server_shutdown", f"Server shutdown after {uptime} uptime")
            
        except Exception as e:
            logger.error(f"❌ Failed to log server shutdown info: {str(e)}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            return {
                "os": f"{psutil.WINDOWS if os.name == 'nt' else psutil.LINUX}",
                "cpu_count": psutil.cpu_count(),
                "total_memory": psutil.virtual_memory().total / (1024**3),  # GB
                "python_version": sys.version.split()[0],
                "process_id": os.getpid(),
                "working_directory": os.getcwd(),
                "startup_time": self.start_time.isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to get system info: {str(e)}")
            return {}
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system performance statistics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / (1024**3),
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "process_memory_mb": self.process.memory_info().rss / (1024**2),
                "process_cpu_percent": self.process.cpu_percent(),
                "open_files": len(self.process.open_files()),
                "connections": len(self.process.connections()),
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get current stats: {str(e)}")
            return {}
    
    def check_system_health(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        try:
            stats = self.get_current_stats()
            alerts = []
            
            # Check CPU usage
            if stats.get("cpu_percent", 0) > self.alert_thresholds["cpu_percent"]:
                alerts.append(f"High CPU usage: {stats['cpu_percent']:.1f}%")
            
            # Check memory usage
            if stats.get("memory_percent", 0) > self.alert_thresholds["memory_percent"]:
                alerts.append(f"High memory usage: {stats['memory_percent']:.1f}%")
            
            # Check disk usage
            if stats.get("disk_percent", 0) > self.alert_thresholds["disk_percent"]:
                alerts.append(f"High disk usage: {stats['disk_percent']:.1f}%")
            
            # Log alerts if any
            if alerts:
                for alert in alerts:
                    logger.warning(f"⚠️ SYSTEM ALERT: {alert}")
                    APILogger.log_system_event("system_alert", alert)
            
            health_status = {
                "status": "healthy" if not alerts else "warning",
                "alerts": alerts,
                "stats": stats,
                "thresholds": self.alert_thresholds
            }
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def start_monitoring(self, interval: int = 300):  # 5 minutes
        """Start continuous system monitoring"""
        self.monitoring_active = True
        logger.info(f"📊 Starting system monitoring (interval: {interval}s)")
        
        try:
            while self.monitoring_active:
                health = self.check_system_health()
                
                if health["status"] == "warning":
                    logger.warning(f"⚠️ System health warning: {len(health['alerts'])} alerts")
                
                await asyncio.sleep(interval)
                
        except Exception as e:
            logger.error(f"❌ System monitoring error: {str(e)}")
        finally:
            logger.info("📊 System monitoring stopped")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring_active = False
    
    def log_database_connection_issue(self, error: Exception, context: str = ""):
        """Log database connection issues with system context"""
        try:
            stats = self.get_current_stats()
            
            logger.error(f"🔌 DATABASE CONNECTION ISSUE")
            logger.error(f"❌ Error: {str(error)}")
            logger.error(f"📍 Context: {context}")
            logger.error(f"📊 System Load - CPU: {stats.get('cpu_percent', 'N/A')}% | Memory: {stats.get('memory_percent', 'N/A')}%")
            logger.error(f"🔗 Process Connections: {stats.get('connections', 'N/A')}")
            
            APILogger.log_system_event(
                "database_connection_failure", 
                f"DB connection failed: {str(error)} | Context: {context}"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to log database connection issue: {str(e)}")
    
    def log_external_service_failure(self, service_name: str, error: Exception, endpoint: str = ""):
        """Log external service failures"""
        try:
            logger.error(f"🌐 EXTERNAL SERVICE FAILURE")
            logger.error(f"🏷️ Service: {service_name}")
            logger.error(f"🔗 Endpoint: {endpoint}")
            logger.error(f"❌ Error: {str(error)}")
            
            APILogger.log_system_event(
                "external_service_failure",
                f"Service: {service_name} | Endpoint: {endpoint} | Error: {str(error)}"
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to log external service failure: {str(e)}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            signal_name = signal.Signals(signum).name
            logger.info(f"📡 Received signal: {signal_name}")
            self.log_server_shutdown(signal_name)
            self.stop_monitoring()
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
        
        if hasattr(signal, 'SIGBREAK'):  # Windows
            signal.signal(signal.SIGBREAK, signal_handler)

# Global system monitor instance
system_monitor = SystemMonitor()
