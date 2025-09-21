"""
Minimal HTTPS Test Script - Direct execution without complex dependencies
"""

import sys
import os
from pathlib import Path

def main():
    print("🚀 Starting Minimal HTTPS Configuration Tests")
    print("="*60)
    
    # Test 1: Basic Python execution
    print("🔍 Test 1: Basic Python execution")
    try:
        import ssl
        import socket
        print("✅ Basic modules imported successfully")
        test1_pass = True
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        test1_pass = False
    
    # Test 2: SSL directory creation
    print("\n🔍 Test 2: SSL directory creation")
    try:
        ssl_dir = Path("ssl")
        ssl_dir.mkdir(exist_ok=True)
        print(f"✅ SSL directory created: {ssl_dir.absolute()}")
        test2_pass = True
    except Exception as e:
        print(f"❌ SSL directory creation failed: {e}")
        test2_pass = False
    
    # Test 3: Check if cryptography is available
    print("\n🔍 Test 3: Cryptography dependency check")
    try:
        import cryptography
        print("✅ Cryptography library is available")
        test3_pass = True
    except ImportError:
        print("❌ Cryptography library not installed")
        print("💡 Install with: pip install cryptography")
        test3_pass = False
    
    # Test 4: SSL config file exists
    print("\n🔍 Test 4: SSL config file check")
    try:
        ssl_config_path = Path("config/ssl_config.py")
        if ssl_config_path.exists():
            print("✅ SSL config file exists")
            test4_pass = True
        else:
            print("❌ SSL config file not found")
            test4_pass = False
    except Exception as e:
        print(f"❌ SSL config check failed: {e}")
        test4_pass = False
    
    # Test 5: Security middleware file exists
    print("\n🔍 Test 5: Security middleware file check")
    try:
        middleware_path = Path("utils/security_middleware.py")
        if middleware_path.exists():
            print("✅ Security middleware file exists")
            test5_pass = True
        else:
            print("❌ Security middleware file not found")
            test5_pass = False
    except Exception as e:
        print(f"❌ Security middleware check failed: {e}")
        test5_pass = False
    
    # Test 6: Main app file exists
    print("\n🔍 Test 6: Main app file check")
    try:
        main_path = Path("main.py")
        if main_path.exists():
            print("✅ Main app file exists")
            test6_pass = True
        else:
            print("❌ Main app file not found")
            test6_pass = False
    except Exception as e:
        print(f"❌ Main app check failed: {e}")
        test6_pass = False
    
    # Test 7: Environment example file
    print("\n🔍 Test 7: Environment example file check")
    try:
        env_path = Path(".env.example")
        if env_path.exists():
            print("✅ Environment example file exists")
            test7_pass = True
        else:
            print("❌ Environment example file not found")
            test7_pass = False
    except Exception as e:
        print(f"❌ Environment file check failed: {e}")
        test7_pass = False
    
    # Summary
    tests = [
        ("Basic Python execution", test1_pass),
        ("SSL directory creation", test2_pass),
        ("Cryptography dependency", test3_pass),
        ("SSL config file", test4_pass),
        ("Security middleware file", test5_pass),
        ("Main app file", test6_pass),
        ("Environment example file", test7_pass)
    ]
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print("="*60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("\n📋 Next Steps:")
        print("1. Install cryptography: pip install cryptography")
        print("2. Run the full HTTPS server: python scripts/https_server.py")
        print("3. Access your secure API at: https://localhost:8443")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        
        if not test3_pass:
            print("\n🔧 CRITICAL: Install cryptography dependency:")
            print("   pip install cryptography")
        
        if not test4_pass or not test5_pass or not test6_pass:
            print("\n🔧 CRITICAL: Missing core files. Please ensure all HTTPS files are created.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
