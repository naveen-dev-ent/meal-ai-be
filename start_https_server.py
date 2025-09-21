"""
HTTPS Server Startup Script
Simple script to start the Money-Health API with HTTPS
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path.cwd()))

def start_server():
    """Start the HTTPS server"""
    print("🚀 Starting Money-Health HTTPS Server")
    print("=" * 50)
    
    try:
        # Import and configure SSL
        from config.ssl_config import ssl_config
        
        print("🔧 Setting up SSL configuration...")
        
        # Generate certificate if needed
        if not ssl_config.validate_ssl_files():
            print("📜 Generating SSL certificate...")
            success = ssl_config.generate_self_signed_cert(
                hostname="localhost",
                ip_addresses=["127.0.0.1"],
                validity_days=365
            )
            if not success:
                print("❌ Failed to generate SSL certificate")
                return False
        
        # Get SSL configuration for Uvicorn
        ssl_config_dict = ssl_config.get_uvicorn_ssl_config()
        
        if ssl_config_dict:
            print("🔐 Starting HTTPS server on port 8443...")
            print("📍 Access your API at: https://localhost:8443")
            print("📖 API Documentation: https://localhost:8443/docs")
            print("🔍 Health Check: https://localhost:8443/health")
            print("\n⚠️  Note: You may see a security warning due to self-signed certificate")
            print("   This is normal for development. Click 'Advanced' -> 'Proceed to localhost'")
            
            # Import and start the server
            import uvicorn
            from main import app
            
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8443,
                log_level="info",
                **ssl_config_dict
            )
        else:
            print("⚠️  SSL configuration empty, starting HTTP server...")
            print("🔓 Starting HTTP server on port 8000...")
            print("📍 Access your API at: http://localhost:8000")
            
            import uvicorn
            from main import app
            
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_level="info"
            )
        
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = start_server()
    sys.exit(0 if success else 1)
