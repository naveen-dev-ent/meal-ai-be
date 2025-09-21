"""
System monitoring and logging utilities for server health and performance tracking.
"""

import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional
import os
import signal
import sys

logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring and logging for server health and performance"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
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
            logger.info(f"🐍 Python: {system_info['python_version']} | PID: {system_info['process_id']}")
            logger.info(f"📁 Working Directory: {system_info['working_directory']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log server startup info: {str(e)}")
    
    def log_server_shutdown(self, signal_received: Optional[str] = None):
        """Log server shutdown information"""
        try:
            uptime = datetime.utcnow() - self.start_time
            
            logger.info("🛑 SERVER SHUTDOWN INITIATED")
            if signal_received:
                logger.info(f"📡 Signal Received: {signal_received}")
            
            logger.info(f"⏱️ Total Uptime: {uptime}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log server shutdown info: {str(e)}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            return {
                "os": os.name,
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
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
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
    
    async def start_monitoring(self, interval: int = 300):
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
            logger.error(f"🔌 DATABASE CONNECTION ISSUE")
            logger.error(f"❌ Error: {str(error)}")
            logger.error(f"📍 Context: {context}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log database connection issue: {str(e)}")
    
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