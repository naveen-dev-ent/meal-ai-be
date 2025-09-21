import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))

print("🔐 Direct HTTPS Configuration Test")
print("=" * 50)

# Test 1: SSL Config Import
print("\n1. Testing SSL Config Import...")
try:
    from config.ssl_config import ssl_config
    print("✅ SSL config imported successfully")
    print(f"   SSL Enabled: {ssl_config.ssl_enabled}")
    print(f"   Auto Generate: {ssl_config.auto_generate_cert}")
    print(f"   Cert Path: {ssl_config.ssl_cert_path}")
    print(f"   Key Path: {ssl_config.ssl_key_path}")
except Exception as e:
    print(f"❌ SSL config import failed: {e}")

# Test 2: Certificate Generation
print("\n2. Testing Certificate Generation...")
try:
    from config.ssl_config import ssl_config
    success = ssl_config.generate_self_signed_cert(
        hostname="localhost",
        ip_addresses=["127.0.0.1"],
        validity_days=365
    )
    if success:
        print("✅ Certificate generated successfully")
        
        # Validate certificate
        if ssl_config.validate_ssl_files():
            print("✅ Certificate validation passed")
            
            # Get certificate info
            cert_info = ssl_config.get_certificate_info()
            if 'error' not in cert_info:
                print(f"✅ Certificate info retrieved")
                print(f"   Subject: {cert_info.get('subject', {}).get('common_name', 'N/A')}")
                print(f"   Valid until: {cert_info.get('valid_until', 'N/A')}")
                print(f"   Days until expiry: {cert_info.get('days_until_expiry', 'N/A')}")
            else:
                print(f"⚠️  Certificate info error: {cert_info.get('error')}")
        else:
            print("❌ Certificate validation failed")
    else:
        print("❌ Certificate generation failed")
except Exception as e:
    print(f"❌ Certificate generation error: {e}")

# Test 3: Security Middleware
print("\n3. Testing Security Middleware...")
try:
    from utils.security_middleware import (
        SecurityHeadersMiddleware,
        HTTPSRedirectMiddleware,
        SecurityAuditMiddleware,
        RateLimitingMiddleware
    )
    print("✅ All security middleware imported successfully")
except Exception as e:
    print(f"❌ Security middleware import failed: {e}")

# Test 4: Main App with HTTPS
print("\n4. Testing Main App with HTTPS...")
try:
    from main import app
    print("✅ Main app imported successfully")
    print(f"   App title: {app.title}")
    print(f"   Servers configured: {len(app.servers) if hasattr(app, 'servers') else 0}")
except Exception as e:
    print(f"❌ Main app import failed: {e}")

# Test 5: SSL Context Creation
print("\n5. Testing SSL Context...")
try:
    from config.ssl_config import ssl_config
    context = ssl_config.get_ssl_context()
    if context:
        print("✅ SSL context created successfully")
        print(f"   Protocol: {getattr(context, 'protocol', 'N/A')}")
        print(f"   Verify mode: {getattr(context, 'verify_mode', 'N/A')}")
    else:
        print("⚠️  SSL context is None (SSL may be disabled)")
except Exception as e:
    print(f"❌ SSL context creation failed: {e}")

# Test 6: Uvicorn SSL Config
print("\n6. Testing Uvicorn SSL Configuration...")
try:
    from config.ssl_config import ssl_config
    uvicorn_config = ssl_config.get_uvicorn_ssl_config()
    if uvicorn_config:
        print("✅ Uvicorn SSL config generated")
        print(f"   SSL keyfile: {uvicorn_config.get('ssl_keyfile', 'N/A')}")
        print(f"   SSL certfile: {uvicorn_config.get('ssl_certfile', 'N/A')}")
    else:
        print("⚠️  Uvicorn SSL config is empty")
except Exception as e:
    print(f"❌ Uvicorn SSL config failed: {e}")

print("\n" + "=" * 50)
print("🎯 Test completed! Check results above.")
print("=" * 50)
