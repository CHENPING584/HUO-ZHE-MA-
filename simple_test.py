#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Starting simple test...")

try:
    from database import SignInDatabase
    db = SignInDatabase()
    print("Database connection successful")
    db.close()
except Exception as e:
    print(f"Database error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed")
