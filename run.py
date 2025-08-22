#!/usr/bin/env python3
"""
HyperAI Builder - Startup Script

Simple script to run the frontend and backend services.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import fastapi
        import uvicorn
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("Please copy .env.template to .env and configure your settings")
        return False
    
    # Check for required variables
    with open(env_file) as f:
        content = f.read()
    
    required_vars = ["SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=" in content and "your-" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing or unconfigured environment variables: {', '.join(missing_vars)}")
        print("Please configure these in your .env file")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting HyperAI Builder Backend...")
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "hyperai_builder.backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        
        print("✅ Backend started successfully")
        print("   📍 URL: http://localhost:8000")
        print("   📚 API Docs: http://localhost:8000/docs")
        
        return backend_process
    
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend."""
    print("🎨 Starting HyperAI Builder Frontend...")
    
    try:
        # Start frontend in background
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "hyperai_builder/frontend/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
        
        print("✅ Frontend started successfully")
        print("   📍 URL: http://localhost:8501")
        
        return frontend_process
    
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function."""
    print("🚀 HyperAI Builder - Starting Services")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        print("⚠️  Continuing anyway, but some features may not work...")
    
    # Start services
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 HyperAI Builder is now running!")
    print("=" * 50)
    print("📍 Frontend: http://localhost:8501")
    print("🔧 Backend:  http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
    
    finally:
        # Cleanup
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()