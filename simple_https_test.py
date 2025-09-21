"""
Simplified HTTPS Test Script
Tests each component individually to identify issues
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_basic_imports():
    """Test basic imports"""
    print("🔍 Testing basic imports...")
    
    try:
        import ssl
        print("✅ ssl module imported")
        
        import socket
        print("✅ socket module imported")
        
        from pathlib import Path
        print("✅ pathlib imported")
        
        return True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_ssl_config_import():
    """Test SSL config import"""
    print("\n🔍 Testing SSL config import...")
    
    try:
        from config.ssl_config import ssl_config
        print("✅ SSL config imported successfully")
        print(f"   SSL Enabled: {ssl_config.ssl_enabled}")
        return True
    except ImportError as e:
        print(f"❌ SSL config import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ SSL config error: {e}")
        return False

def test_cryptography_dependency():
    """Test cryptography dependency"""
    print("\n🔍 Testing cryptography dependency...")
    
    try:
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes
        print("✅ Cryptography library available")
        return True
    except ImportError as e:
        print(f"❌ Cryptography not available: {e}")
        print("💡 Install with: pip install cryptography")
        return False

def test_ssl_directory():
    """Test SSL directory creation"""
    print("\n🔍 Testing SSL directory...")
    
    try:
        ssl_dir = Path("ssl")
        ssl_dir.mkdir(exist_ok=True)
        print(f"✅ SSL directory created: {ssl_dir.absolute()}")
        return True
    except Exception as e:
        print(f"❌ SSL directory creation failed: {e}")
        return False

def test_certificate_generation():
    """Test certificate generation"""
    print("\n🔍 Testing certificate generation...")
    
    try:
        from config.ssl_config import ssl_config
        
        # Only test if cryptography is available
        try:
            from cryptography import x509
        except ImportError:
            print("⚠️  Skipping certificate generation (cryptography not available)")
            return True
        
        success = ssl_config.generate_self_signed_cert(
            hostname="localhost",
            ip_addresses=["127.0.0.1"],
            validity_days=365
        )
        
        if success:
            print("✅ Certificate generation successful")
            return True
        else:
            print("❌ Certificate generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Certificate generation error: {e}")
        return False

def test_security_middleware_import():
    """Test security middleware import"""
    print("\n🔍 Testing security middleware import...")
    
    try:
        from utils.security_middleware import SecurityHeadersMiddleware
        print("✅ Security middleware imported")
        return True
    except ImportError as e:
        print(f"❌ Security middleware import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Security middleware error: {e}")
        return False

def test_main_app_import():
    """Test main app import"""
    print("\n🔍 Testing main app import...")
    
    try:
        # Test if we can import main components
        from main import app
        print("✅ Main app imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Main app import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Main app error: {e}")
        return False

def run_simple_tests():
    """Run simplified tests"""
    print("🚀 Starting Simplified HTTPS Tests\n")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Cryptography Dependency", test_cryptography_dependency),
        ("SSL Directory", test_ssl_directory),
        ("SSL Config Import", test_ssl_config_import),
        ("Certificate Generation", test_certificate_generation),
        ("Security Middleware Import", test_security_middleware_import),
        ("Main App Import", test_main_app_import)
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
    print("\n" + "="*50)
    print("📊 SIMPLIFIED TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All simplified tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)
