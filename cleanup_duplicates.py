#!/usr/bin/env python3
"""
Script to clean up duplicate directories in the backend
"""

import os
import shutil
from pathlib import Path

def main():
    backend_dir = Path(__file__).parent
    
    # Directories to remove (duplicates/backups)
    dirs_to_remove = [
        "app_backup",
        "src_backup", 
        "models",  # Empty directory
    ]
    
    # Files to remove (test files)
    files_to_remove = [
        "direct_https_test.py",
        "simple_https_test.py", 
        "start_https_server.py",
        "test_connection.py",
        "test_db.py",
        "test_https_minimal.py",
        "test_https_setup.py",
        "test_validation.py",
        "validate_https.py"
    ]
    
    print("🧹 Cleaning up duplicate directories and test files...")
    
    # Remove duplicate directories
    for dir_name in dirs_to_remove:
        dir_path = backend_dir / dir_name
        if dir_path.exists():
            print(f"🗑️  Removing directory: {dir_name}")
            shutil.rmtree(dir_path)
        else:
            print(f"✅ Directory already clean: {dir_name}")
    
    # Remove test files
    for file_name in files_to_remove:
        file_path = backend_dir / file_name
        if file_path.exists():
            print(f"🗑️  Removing file: {file_name}")
            file_path.unlink()
        else:
            print(f"✅ File already clean: {file_name}")
    
    # Clean up test directories in utils
    utils_test_files = [
        "utils/comprehensive_api_test.py",
        "utils/debug_schemas.py", 
        "utils/final_api_validation.py",
        "utils/simple_test.py",
        "utils/testing_tools.py"
    ]
    
    for file_path in utils_test_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"🗑️  Removing test file: {file_path}")
            full_path.unlink()
    
    print("✅ Cleanup completed!")
    print("\n📁 Current structure:")
    print("├── src/           # Main application code")
    print("├── config/        # Configuration files") 
    print("├── utils/         # Utility functions")
    print("├── tests/         # Test files")
    print("├── logs/          # Log files")
    print("├── data/          # Database files")
    print("└── main.py        # Application entry point")

if __name__ == "__main__":
    main()