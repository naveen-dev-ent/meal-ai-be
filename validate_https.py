#!/usr/bin/env python3
"""
HTTPS Configuration Validator
Comprehensive validation of all HTTPS/SSL components
"""

import os
import sys
import traceback
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and return result"""
    try:
        path = Path(file_path)
        exists = path.exists()
        if exists:
            size = path.stat().st_size
            print(f"✅ {description}: {file_path} ({size} bytes)")
        else:
            print(f"❌ {description}: {file_path} (NOT FOUND)")
        return exists
    except Exception as e:
        print(f"❌ {description}: Error checking {file_path} - {e}")
        return False

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False
    except Exception as e:
        print(f"❌ {description}: {module_name} - Unexpected error: {e}")
        return False

def check_dependency(package_name):
    """Check if a package dependency is available"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("🔐 HTTPS Configuration Validator")
    print("=" * 60)
    
    results = []
    
    # 1. Check core files exist
    print("\n📁 Checking Core Files:")
    files_to_check = [
        ("config/ssl_config.py", "SSL Configuration"),
        ("utils/security_middleware.py", "Security Middleware"),
        ("scripts/https_server.py", "HTTPS Server Script"),
        ("main.py", "Main Application"),
        (".env.example", "Environment Example"),
        ("requirements.txt", "Requirements File")
    ]
    
    file_results = []
    for file_path, description in files_to_check:
        result = check_file_exists(file_path, description)
        file_results.append(result)
        results.append((f"File: {description}", result))
    
    # 2. Check dependencies
    print("\n📦 Checking Dependencies:")
    dependencies = [
        ("ssl", "SSL Module (built-in)"),
        ("socket", "Socket Module (built-in)"),
        ("pathlib", "Path Module (built-in)"),
        ("fastapi", "FastAPI Framework"),
        ("uvicorn", "Uvicorn Server"),
        ("cryptography", "Cryptography Library")
    ]
    
    dep_results = []
    for package, description in dependencies:
        result = check_import(package, description)
        dep_results.append(result)
        results.append((f"Dependency: {description}", result))
    
    # 3. Check SSL directory
    print("\n📂 Checking SSL Directory:")
    try:
        ssl_dir = Path("ssl")
        ssl_dir.mkdir(exist_ok=True)
        print(f"✅ SSL Directory: {ssl_dir.absolute()}")
        ssl_dir_result = True
    except Exception as e:
        print(f"❌ SSL Directory: Failed to create - {e}")
        ssl_dir_result = False
    
    results.append(("SSL Directory Creation", ssl_dir_result))
    
    # 4. Test SSL configuration (if cryptography is available)
    print("\n🔧 Testing SSL Configuration:")
    ssl_config_result = False
    if check_dependency("cryptography"):
        try:
            sys.path.insert(0, str(Path.cwd()))
            from config.ssl_config import ssl_config
            print(f"✅ SSL Config Import: Successful")
            print(f"   SSL Enabled: {ssl_config.ssl_enabled}")
            print(f"   Auto Generate: {ssl_config.auto_generate_cert}")
            ssl_config_result = True
        except Exception as e:
            print(f"❌ SSL Config Import: {e}")
            ssl_config_result = False
    else:
        print("⚠️  SSL Config Test: Skipped (cryptography not available)")
        ssl_config_result = True  # Don't fail if dependency missing
    
    results.append(("SSL Configuration", ssl_config_result))
    
    # 5. Test security middleware
    print("\n🛡️  Testing Security Middleware:")
    try:
        from utils.security_middleware import SecurityHeadersMiddleware
        print("✅ Security Middleware: Import successful")
        middleware_result = True
    except Exception as e:
        print(f"❌ Security Middleware: {e}")
        middleware_result = False
    
    results.append(("Security Middleware", middleware_result))
    
    # 6. Test main app configuration
    print("\n🚀 Testing Main App:")
    try:
        from main import app
        print("✅ Main App: Import successful")
        print(f"   App Title: {app.title}")
        main_app_result = True
    except Exception as e:
        print(f"❌ Main App: {e}")
        main_app_result = False
    
    results.append(("Main Application", main_app_result))
    
    # 7. Check environment configuration
    print("\n⚙️  Checking Environment Configuration:")
    env_file = Path(".env.example")
    if env_file.exists():
        try:
            content = env_file.read_text()
            ssl_configs = ["SSL_ENABLED", "SSL_CERT_PATH", "HTTPS_PORT"]
            found_configs = [config for config in ssl_configs if config in content]
            
            if len(found_configs) == len(ssl_configs):
                print(f"✅ Environment Config: All SSL settings found")
                env_result = True
            else:
                missing = set(ssl_configs) - set(found_configs)
                print(f"⚠️  Environment Config: Missing {missing}")
                env_result = True  # Warning, not failure
        except Exception as e:
            print(f"❌ Environment Config: {e}")
            env_result = False
    else:
        print("❌ Environment Config: .env.example not found")
        env_result = False
    
    results.append(("Environment Configuration", env_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<35} {status}")
    
    print("=" * 60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if not check_dependency("cryptography"):
        print("🔧 CRITICAL: Install cryptography dependency:")
        print("   pip install cryptography")
    
    if passed == total:
        print("🎉 All validations passed! Your HTTPS setup is ready.")
        print("\n🚀 To start your secure server:")
        print("   python scripts/https_server.py --mode https")
        print("   Access at: https://localhost:8443")
    else:
        print("⚠️  Some validations failed. Address the issues above.")
        
        if not any(dep_results):
            print("🔧 Install missing dependencies:")
            print("   pip install -r requirements.txt")
        
        if not any(file_results):
            print("🔧 Ensure all HTTPS configuration files are created.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
    except Exception as e:
        print(f"\n💥 VALIDATION FAILED WITH EXCEPTION:")
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        exit_code = 2
    
    print(f"\nExit Code: {exit_code}")
    sys.exit(exit_code)
