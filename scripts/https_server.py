"""
HTTPS Server Startup Script
Handles SSL certificate generation and secure server startup
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from config.ssl_config import ssl_config
from config.logging_config import logger

def setup_ssl_certificates():
    """Setup SSL certificates for HTTPS"""
    try:
        logger.info("🔐 Setting up SSL certificates...")
        
        # Check if certificates exist and are valid
        if ssl_config.validate_ssl_files():
            logger.info("✅ Valid SSL certificates found")
            return True
        
        # Generate self-signed certificates for development
        if ssl_config.auto_generate_cert:
            logger.info("🔧 Generating self-signed SSL certificates...")
            success = ssl_config.generate_self_signed_cert(
                hostname="localhost",
                ip_addresses=["127.0.0.1"],
                validity_days=365
            )
            
            if success:
                logger.info("✅ SSL certificates generated successfully")
                return True
            else:
                logger.error("❌ Failed to generate SSL certificates")
                return False
        else:
            logger.error("❌ SSL certificates not found and auto-generation disabled")
            return False
            
    except Exception as e:
        logger.error(f"❌ SSL setup failed: {e}")
        return False

def start_https_server():
    """Start the HTTPS server"""
    try:
        # Setup SSL certificates
        if not setup_ssl_certificates():
            logger.error("❌ Cannot start HTTPS server without valid SSL certificates")
            return False
        
        # Get SSL configuration
        ssl_config_dict = ssl_config.get_uvicorn_ssl_config()
        
        if not ssl_config_dict:
            logger.error("❌ SSL configuration is empty")
            return False
        
        logger.info("🚀 Starting HTTPS server on port 8443...")
        
        # Import and run the main app
        from main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8443,
            reload=True,
            log_level="info",
            **ssl_config_dict
        )
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to start HTTPS server: {e}")
        return False

def start_dual_servers():
    """Start both HTTP (redirect) and HTTPS servers"""
    try:
        logger.info("🔄 Starting dual HTTP/HTTPS servers...")
        
        # Setup SSL certificates
        if not setup_ssl_certificates():
            logger.warning("⚠️  SSL setup failed, starting HTTP only")
            start_http_server()
            return
        
        # Start HTTPS server in main process
        logger.info("🔐 Starting HTTPS server on port 8443...")
        
        from main import app
        import uvicorn
        
        ssl_config_dict = ssl_config.get_uvicorn_ssl_config()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8443,
            reload=True,
            log_level="info",
            **ssl_config_dict
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start dual servers: {e}")

def start_http_server():
    """Start HTTP server (for development/fallback)"""
    try:
        logger.info("🔓 Starting HTTP server on port 8000...")
        
        from main import app
        import uvicorn
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start HTTP server: {e}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Money-Health HTTPS Server")
    parser.add_argument(
        "--mode",
        choices=["https", "http", "dual"],
        default="https",
        help="Server mode: https (HTTPS only), http (HTTP only), dual (both)"
    )
    parser.add_argument(
        "--generate-cert",
        action="store_true",
        help="Force generation of new SSL certificate"
    )
    
    args = parser.parse_args()
    
    # Force certificate generation if requested
    if args.generate_cert:
        logger.info("🔧 Forcing SSL certificate generation...")
        ssl_config.generate_self_signed_cert()
    
    # Start server based on mode
    if args.mode == "https":
        start_https_server()
    elif args.mode == "http":
        start_http_server()
    elif args.mode == "dual":
        start_dual_servers()

if __name__ == "__main__":
    main()
