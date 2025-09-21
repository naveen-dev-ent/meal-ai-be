"""
File organization utility to move existing files to proper directories.
"""

import os
import shutil
from pathlib import Path


def organize_backend_files():
    """Organize all backend files into proper directory structure"""
    
    backend_root = Path(__file__).parent.parent
    
    # File organization mapping
    file_moves = {
        # Move test and validation files to utils
        "comprehensive_api_test.py": "utils/comprehensive_api_test.py",
        "debug_schemas.py": "utils/debug_schemas.py", 
        "final_api_validation.py": "utils/final_api_validation.py",
        "simple_test.py": "utils/simple_test.py",
        
        # Move data files to appropriate locations
        "dummy_test_data.json": "utils/dummy_test_data.json",
    }
    
    print("📁 ORGANIZING BACKEND FILES")
    print("=" * 40)
    
    moved_files = []
    
    for source_file, destination in file_moves.items():
        source_path = backend_root / source_file
        dest_path = backend_root / destination
        
        if source_path.exists():
            try:
                # Create destination directory if it doesn't exist
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Move the file
                shutil.move(str(source_path), str(dest_path))
                moved_files.append(f"✅ {source_file} → {destination}")
                
            except Exception as e:
                print(f"❌ Failed to move {source_file}: {e}")
        else:
            print(f"⚠️  File not found: {source_file}")
    
    # Print results
    for move in moved_files:
        print(move)
    
    print(f"\n📊 SUMMARY: {len(moved_files)} files organized")
    print("=" * 40)
    
    return moved_files


def create_directory_structure():
    """Create proper directory structure with __init__.py files"""
    
    backend_root = Path(__file__).parent.parent
    
    directories = [
        "scripts",
        "utils", 
        "docs",
        "config",
        "migrations"
    ]
    
    print("📂 CREATING DIRECTORY STRUCTURE")
    print("=" * 40)
    
    for directory in directories:
        dir_path = backend_root / directory
        init_file = dir_path / "__init__.py"
        
        # Create directory
        dir_path.mkdir(exist_ok=True)
        
        # Create __init__.py if it doesn't exist
        if not init_file.exists():
            with open(init_file, 'w') as f:
                f.write(f'"""\n{directory.title()} package for backend organization.\n"""\n')
            print(f"✅ Created {directory}/__init__.py")
        else:
            print(f"📁 {directory}/ already exists")
    
    print("=" * 40)


def update_gitignore():
    """Update .gitignore with proper patterns for organized structure"""
    
    backend_root = Path(__file__).parent.parent
    gitignore_path = backend_root / ".gitignore"
    
    additional_patterns = [
        "\n# Organized structure patterns",
        "utils/test_data_generated.json",
        "utils/api_test_results.json", 
        "docs/api_documentation.json",
        "scripts/database_backup.db",
        "migrations/*.pyc",
        "config/local_settings.py"
    ]
    
    if gitignore_path.exists():
        with open(gitignore_path, 'a') as f:
            f.write('\n'.join(additional_patterns))
        print("✅ Updated .gitignore with organized structure patterns")
    else:
        print("⚠️  .gitignore not found")


if __name__ == "__main__":
    create_directory_structure()
    organize_backend_files()
    update_gitignore()
    
    print("\n🎉 BACKEND ORGANIZATION COMPLETE!")
    print("📁 All files properly structured and organized")
