#!/usr/bin/env python3
"""Fix yash user role"""

import sqlite3

DATABASE = 'users.db'

def fix_yash_role():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Update yash to be a student with proper role
    c.execute("""
        UPDATE users 
        SET role = 'student' 
        WHERE username = 'yash'
    """)
    conn.commit()
    
    print("✅ User 'yash' updated successfully!")
    
    # Verify the update
    c.execute("SELECT username, password, role, paid, class_id FROM users WHERE username = 'yash'")
    user = c.fetchone()
    
    if user:
        print(f"\n📋 Updated User Details:")
        print(f"   Username: {user[0]}")
        print(f"   Password: {user[1]}")
        print(f"   Role: {user[2]}")
        print(f"   Paid Status: {user[3]}")
        print(f"   Class ID: {user[4]}")
    
    conn.close()

if __name__ == "__main__":
    fix_yash_role()
