#!/usr/bin/env python3
"""
Simple script to remove only duplicate directories
"""

import os
import shutil
from pathlib import Path

def main():
    backend_dir = Path(__file__).parent
    
    # Only remove duplicate directories
    dirs_to_remove = [
        "app_backup",
        "src_backup"
    ]
    
    print("Cleaning up duplicate directories...")
    
    for dir_name in dirs_to_remove:
        dir_path = backend_dir / dir_name
        if dir_path.exists():
            print(f"Removing duplicate directory: {dir_name}")
            shutil.rmtree(dir_path)
        else:
            print(f"Directory not found: {dir_name}")
    
    print("Cleanup completed!")

if __name__ == "__main__":
    main()