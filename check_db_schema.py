#!/usr/bin/env python3
"""Quick script to check database schema and user 'yash'"""

import sqlite3

DATABASE = 'users.db'

def check_user():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # First, check the schema
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    print("📋 Users table columns:")
    for col in columns:
        print(f"   - {col['name']} ({col['type']})")
    
    print("\n" + "="*60)
    
    # Check if user 'yash' exists
    c.execute("SELECT * FROM users WHERE username = 'yash'")
    user = c.fetchone()
    
    if user:
        print("\n✅ User 'yash' exists!")
        for key in user.keys():
            print(f"   {key}: {user[key]}")
    else:
        print("\n❌ User 'yash' not found in database")
        print("\n📝 Sample users:")
        c.execute("SELECT username, role FROM users LIMIT 5")
        users = c.fetchall()
        for u in users:
            print(f"   - {u['username']} ({u['role']})")
    
    conn.close()

if __name__ == "__main__":
    check_user()
