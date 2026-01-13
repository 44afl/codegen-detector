"""
Simple SQL Injection Test using AuthDB
Demonstrates a SQL injection attempt and how AuthDB protects against it
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.auth_db import AuthDB


def main():
    db = AuthDB('test_injection.db')
    
    try:
        db.create_user('admin@example.com', 'securepassword', 'Admin User')
        print("[Setup] Created test user: admin@example.com")
    except:
        print("[Setup] User already exists")
    
    print("\n" + "=" * 60)
    print("SQL INJECTION TEST")
    print("=" * 60)
    
    print("\n1. Normal query:")
    user = db.get_user_by_email('admin@example.com')
    if user:
        print(f"   Found user: {user['email']}")
    
    print("\n2. SQL Injection attempt with: admin@example.com' OR '1'='1")
    try:
        malicious_input = "admin@example.com' OR '1'='1"
        user = db.get_user_by_email(malicious_input)
        if user:
            print(f"   [VULNERABILITY!] Attack succeeded: {user}")
        else:
            print("   [PROTECTED] No user found - injection failed")
    except ValueError as e:
        print(f"   [PROTECTED] {e}")
    
    print("\n3. SQL Injection attempt using _execute with UPDATE:")
    try:
        # Attempt to inject malicious SQL via _execute
        malicious_query = "UPDATE users SET is_active = 1 WHERE email = 'admin@example.com'; DROP TABLE users--"
        result = db._execute(malicious_query)
        print(f"   [VULNERABILITY!] Malicious query executed: {result}")
    except ValueError as e:
        print(f"   [PROTECTED] {e}")
    
    print("\n4. SQL Injection attempt using _execute with DELETE:")
    try:
        # Attempt SQL injection with comment bypass
        malicious_query = "DELETE FROM users WHERE email = 'admin@example.com'--"
        result = db._execute(malicious_query)
        print(f"   [VULNERABILITY!] Malicious DELETE executed: {result}")
    except ValueError as e:
        print(f"   [PROTECTED] {e}")
    
    import os
    if os.path.exists('test_injection.db'):
        os.remove('test_injection.db')
        print("\n[Cleanup] Removed test database")


if __name__ == "__main__":
    main()
