import os
import re
from pathlib import Path

# Define the base directory of your project
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / 'src'

# Define the import patterns to update
IMPORT_REPLACEMENTS = [
    (r'from\s+app\.', 'from src.'),
    (r'from\s+utils\.', 'from src.utils.'),
    (r'from\s+core\.', 'from src.core.'),
    (r'from\s+models\.', 'from src.models.'),
    (r'from\s+schemas\.', 'from src.schemas.'),
    (r'from\s+middleware\.', 'from src.middleware.'),
    (r'from\s+api\.', 'from src.api.'),
]

def update_file_imports(file_path):
    """Update imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all replacements
        for pattern, replacement in IMPORT_REPLACEMENTS:
            content = re.sub(pattern, replacement, content)
        
        # Only write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    # Find all Python files in the src directory
    python_files = list(SRC_DIR.rglob('*.py'))
    updated_count = 0
    
    print(f"Found {len(python_files)} Python files to check...")
    
    for py_file in python_files:
        if update_file_imports(py_file):
            updated_count += 1
    
    print(f"\nUpdate complete! {updated_count} files were updated.")

if __name__ == '__main__':
    main()
