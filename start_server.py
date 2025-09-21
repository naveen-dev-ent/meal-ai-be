#!/usr/bin/env python3
"""
Simple script to start the Money Health backend server
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Starting Money Health Backend Server...")
    print(f"📁 Working directory: {backend_dir}")
    
    # Check if virtual environment exists
    venv_path = backend_dir / "venv"
    if venv_path.exists():
        print("✅ Virtual environment found")
        if os.name == 'nt':  # Windows
            python_exe = venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            python_exe = venv_path / "bin" / "python"
    else:
        print("⚠️  No virtual environment found, using system Python")
        python_exe = sys.executable
    
    # Check if requirements are installed
    try:
        subprocess.run([str(python_exe), "-c", "import fastapi, uvicorn"], 
                      check=True, capture_output=True)
        print("✅ Required packages found")
    except subprocess.CalledProcessError:
        print("❌ Missing required packages. Installing...")
        subprocess.run([str(python_exe), "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
    
    # Start the server
    print("🌐 Starting server on http://localhost:8000")
    print("📚 API docs will be available at http://localhost:8000/docs")
    print("🔍 Health check at http://localhost:8000/health")
    print("\n💡 Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([
            str(python_exe), "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())