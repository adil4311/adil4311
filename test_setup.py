#!/usr/bin/env python3
"""
HyperAI Builder - Setup Test Script

Simple test to verify that the application is properly configured.
"""

import os
import sys
import importlib
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    required_modules = [
        "streamlit",
        "fastapi", 
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "openai",
        "anthropic",
        "google.generativeai"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All required modules imported successfully")
    return True

def test_hyperai_modules():
    """Test if HyperAI Builder modules can be imported."""
    print("\n🧪 Testing HyperAI Builder modules...")
    
    # Add parent directory to path
    sys.path.append(str(Path(__file__).parent))
    
    try:
        from hyperai_builder.core.config import get_settings
        print("  ✅ Core configuration")
        
        from hyperai_builder.core.logging import setup_logging
        print("  ✅ Core logging")
        
        from hyperai_builder.models.base import Base
        print("  ✅ Database models")
        
        from hyperai_builder.ai.models import BaseAIModel
        print("  ✅ AI models")
        
        print("✅ All HyperAI Builder modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import HyperAI Builder modules: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("\n🧪 Testing environment configuration...")
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ .env file exists")
        
        # Check for required variables
        with open(env_file) as f:
            content = f.read()
        
        required_vars = ["SECRET_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=" in content and "your-" in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"  ⚠️  Missing/unconfigured variables: {', '.join(missing_vars)}")
        else:
            print("  ✅ Environment variables configured")
    else:
        print("  ⚠️  .env file not found (copy from .env.template)")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 11):
        print(f"  ✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"  ❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} (3.11+ required)")
        return False
    
    return True

def test_database():
    """Test database connection."""
    print("\n🧪 Testing database connection...")
    
    try:
        from hyperai_builder.backend.core.database import db_manager
        
        # Test connection
        if db_manager.test_connection():
            print("  ✅ Database connection successful")
            return True
        else:
            print("  ❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"  ❌ Database test error: {e}")
        return False

def test_ai_models():
    """Test AI model factory."""
    print("\n🧪 Testing AI model factory...")
    
    try:
        from hyperai_builder.ai.models import ai_model_factory
        
        # List available providers
        providers = ai_model_factory.list_providers()
        print(f"  ✅ Available AI providers: {', '.join(providers)}")
        
        # Check if OpenAI is available
        if "openai" in providers:
            print("  ✅ OpenAI integration available")
        
        if "anthropic" in providers:
            print("  ✅ Anthropic integration available")
        
        if "google" in providers:
            print("  ✅ Google AI integration available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI model test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 HyperAI Builder - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("HyperAI Modules", test_hyperai_modules),
        ("Environment", test_environment),
        ("Database", test_database),
        ("AI Models", test_ai_models)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                print(f"  ❌ {test_name} failed")
        except Exception as e:
            print(f"  ❌ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! HyperAI Builder is ready to use.")
        print("\n🚀 To start the application:")
        print("   python run.py")
        print("\n   Or start services individually:")
        print("   Frontend: streamlit run hyperai_builder/frontend/app.py")
        print("   Backend:  uvicorn hyperai_builder.backend.main:app --reload")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n💡 Common solutions:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Copy .env.template to .env and configure")
        print("   3. Check Python version (3.11+ required)")
        print("   4. Ensure all files are in the correct directory structure")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)