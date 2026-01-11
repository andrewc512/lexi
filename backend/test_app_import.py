#!/usr/bin/env python3
"""
Diagnostic script to test if the FastAPI app can be imported correctly.
Run this to identify import errors before starting uvicorn.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Testing FastAPI App Import")
print("=" * 60)

try:
    print("\n1. Testing Python version...")
    print(f"   Python: {sys.version}")
    print(f"   Python path: {sys.executable}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

try:
    print("\n2. Testing FastAPI import...")
    from fastapi import FastAPI
    print(f"   ✅ FastAPI imported successfully")
except ImportError as e:
    print(f"   ❌ Failed to import FastAPI: {e}")
    print("   💡 Run: pip install fastapi")
    sys.exit(1)

try:
    print("\n3. Testing app.core.config import...")
    from app.core.config import settings
    print(f"   ✅ Config imported successfully")
    print(f"   SUPABASE_URL: {'✅ Set' if settings.SUPABASE_URL else '❌ Missing'}")
    print(f"   SUPABASE_KEY: {'✅ Set' if settings.SUPABASE_KEY else '❌ Missing'}")
except Exception as e:
    print(f"   ❌ Failed to import config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n4. Testing API router imports...")
    from app.api import health
    print("   ✅ health router imported")
except Exception as e:
    print(f"   ❌ Failed to import health router: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.api import interviews
    print("   ✅ interviews router imported")
except Exception as e:
    print(f"   ❌ Failed to import interviews router: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.api import session
    print("   ✅ session router imported")
except Exception as e:
    print(f"   ❌ Failed to import session router: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.api import ai
    print("   ✅ ai router imported")
except Exception as e:
    print(f"   ❌ Failed to import ai router: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.api import email
    print("   ✅ email router imported")
except Exception as e:
    print(f"   ❌ Failed to import email router: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from app.api import realtime
    print("   ✅ realtime router imported")
except Exception as e:
    print(f"   ❌ Failed to import realtime router: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n5. Testing main app import...")
    from app.main import app
    print(f"   ✅ App imported successfully!")
    print(f"   App type: {type(app)}")
    print(f"   App title: {app.title}")
except Exception as e:
    print(f"   ❌ Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All imports successful! The app should work.")
print("=" * 60)
print("\nYou can now run:")
print("  uvicorn app.main:app --reload")
print("\n")
