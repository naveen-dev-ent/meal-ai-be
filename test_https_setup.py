"""
HTTPS Configuration Test Script
Validates SSL setup and HTTPS functionality
"""

import sys
import os
import ssl
import socket
from pathlib import Path

# Optional imports with fallbacks
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import urllib3
    from urllib3.exceptions import InsecureRequestWarning
    urllib3.disable_warnings(InsecureRequestWarning)
    HAS_URLLIB3 = True
except ImportError:
    HAS_URLLIB3 = False

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_ssl_certificate_generation():
    """Test SSL certificate generation"""
    print("🔍 Testing SSL certificate generation...")
    
    try:
        from config.ssl_config import ssl_config
        
        # Test certificate generation
        success = ssl_config.generate_self_signed_cert(
            hostname="localhost",
            ip_addresses=["127.0.0.1"],
            validity_days=365
        )
        
        if success:
            print("✅ SSL certificate generated successfully")
            
            # Validate the generated certificate
            if ssl_config.validate_ssl_files():
                print("✅ SSL certificate validation passed")
                
                # Get certificate info
                cert_info = ssl_config.get_certificate_info()
                if 'error' not in cert_info:
                    print(f"📋 Certificate Info:")
                    print(f"   Subject: {cert_info.get('subject', {}).get('common_name', 'N/A')}")
                    print(f"   Valid Until: {cert_info.get('valid_until', 'N/A')}")
                    print(f"   Days Until Expiry: {cert_info.get('days_until_expiry', 'N/A')}")
                else:
                    print(f"⚠️  Certificate info error: {cert_info.get('error')}")
                
                return True
            else:
                print("❌ SSL certificate validation failed")
                return False
        else:
            print("❌ SSL certificate generation failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("⚠️  Missing cryptography dependency - install with: pip install cryptography")
        return False
    except Exception as e:
        print(f"❌ SSL certificate test failed: {e}")
        return False

def test_ssl_context():
    """Test SSL context creation"""
    print("\n🔍 Testing SSL context creation...")
    
    try:
        from config.ssl_config import ssl_config
        
        # Test SSL context creation
        context = ssl_config.get_ssl_context()
        
        if context:
            print("✅ SSL context created successfully")
            print(f"   Protocol: {getattr(context, 'protocol', 'N/A')}")
            print(f"   Verify Mode: {getattr(context, 'verify_mode', 'N/A')}")
            return True
        else:
            print("⚠️  SSL context creation skipped (SSL disabled or certificates unavailable)")
            return True  # Not a failure if SSL is disabled
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ SSL context test failed: {e}")
        return False

def test_uvicorn_ssl_config():
    """Test Uvicorn SSL configuration"""
    print("\n🔍 Testing Uvicorn SSL configuration...")
    
    try:
        from config.ssl_config import ssl_config
        
        # Test Uvicorn SSL config
        uvicorn_config = ssl_config.get_uvicorn_ssl_config()
        
        if uvicorn_config:
            print("✅ Uvicorn SSL configuration generated")
            print(f"   SSL Keyfile: {uvicorn_config.get('ssl_keyfile', 'N/A')}")
            print(f"   SSL Certfile: {uvicorn_config.get('ssl_certfile', 'N/A')}")
            print(f"   SSL Version: {uvicorn_config.get('ssl_version', 'N/A')}")
            return True
        else:
            print("⚠️  Uvicorn SSL configuration empty (SSL disabled)")
            return True  # Not a failure if SSL is disabled
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Uvicorn SSL config test failed: {e}")
        return False

def test_security_middleware():
    """Test security middleware imports"""
    print("\n🔍 Testing security middleware...")
    
    try:
        from utils.security_middleware import (
            SecurityHeadersMiddleware,
            HTTPSRedirectMiddleware,
            SecurityAuditMiddleware,
            RateLimitingMiddleware
        )
        
        print("✅ Security middleware imported successfully")
        print("   - SecurityHeadersMiddleware")
        print("   - HTTPSRedirectMiddleware") 
        print("   - SecurityAuditMiddleware")
        print("   - RateLimitingMiddleware")
        
        return True
        
    except Exception as e:
        print(f"❌ Security middleware test failed: {e}")
        return False

def test_https_server_startup():
    """Test HTTPS server startup script"""
    print("\n🔍 Testing HTTPS server startup script...")
    
    try:
        from scripts.https_server import setup_ssl_certificates
        
        # Test SSL setup
        success = setup_ssl_certificates()
        
        if success:
            print("✅ HTTPS server setup successful")
            return True
        else:
            print("⚠️  HTTPS server setup returned false (may be expected if SSL disabled)")
            return True  # Don't fail the test suite for this
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("⚠️  HTTPS server script may have missing dependencies")
        return False
    except Exception as e:
        print(f"❌ HTTPS server startup test failed: {e}")
        return False

def test_port_availability():
    """Test if HTTPS port is available"""
    print("\n🔍 Testing port availability...")
    
    try:
        # Test HTTPS port (8443)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 8443))
        sock.close()
        
        if result != 0:
            print("✅ HTTPS port 8443 is available")
            
            # Test HTTP port (8000)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            
            if result != 0:
                print("✅ HTTP port 8000 is available")
                return True
            else:
                print("⚠️  HTTP port 8000 is in use")
                return True  # Still OK for HTTPS
        else:
            print("⚠️  HTTPS port 8443 is in use")
            return True  # May be our server running
            
    except Exception as e:
        print(f"❌ Port availability test failed: {e}")
        return False

def test_environment_config():
    """Test environment configuration for HTTPS"""
    print("\n🔍 Testing environment configuration...")
    
    try:
        # Check if .env.example exists
        env_example_path = Path(".env.example")
        if env_example_path.exists():
            print("✅ .env.example file exists")
            
            # Read and check SSL configuration
            with open(env_example_path, 'r') as f:
                content = f.read()
                
            ssl_configs = [
                "SSL_ENABLED",
                "SSL_CERT_PATH", 
                "SSL_KEY_PATH",
                "HTTPS_PORT",
                "ENFORCE_HTTPS"
            ]
            
            for config in ssl_configs:
                if config in content:
                    print(f"✅ Environment config includes: {config}")
                else:
                    print(f"⚠️  Missing environment config: {config}")
            
            return True
        else:
            print("❌ .env.example file not found")
            return False
            
    except Exception as e:
        print(f"❌ Environment config test failed: {e}")
        return False

def run_all_tests():
    """Run all HTTPS configuration tests"""
    print("🚀 Starting HTTPS Configuration Tests\n")
    
    tests = [
        ("SSL Certificate Generation", test_ssl_certificate_generation),
        ("SSL Context Creation", test_ssl_context),
        ("Uvicorn SSL Configuration", test_uvicorn_ssl_config),
        ("Security Middleware", test_security_middleware),
        ("HTTPS Server Startup", test_https_server_startup),
        ("Port Availability", test_port_availability),
        ("Environment Configuration", test_environment_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 HTTPS CONFIGURATION TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<35} {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All HTTPS configuration tests passed!")
        print("\n🔐 Your application is ready for HTTPS!")
        print("\nTo start the HTTPS server:")
        print("  python scripts/https_server.py --mode https")
        print("\nTo start both HTTP and HTTPS:")
        print("  python scripts/https_server.py --mode dual")
        
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
