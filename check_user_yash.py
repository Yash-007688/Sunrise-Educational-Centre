#!/usr/bin/env python3
"""Quick script to check if user 'yash' exists and create if needed"""

import sqlite3

DATABASE = 'users.db'

def check_and_create_user():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Check if user 'yash' exists
    c.execute("SELECT username, password, role, class FROM users WHERE username = 'yash'")
    user = c.fetchone()
    
    if user:
        print(f"✅ User 'yash' exists!")
        print(f"   Username: {user[0]}")
        print(f"   Password: {user[1]}")
        print(f"   Role: {user[2]}")
        print(f"   Class: {user[3]}")
    else:
        print("❌ User 'yash' not found. Creating...")
        
        # Create user 'yash' with password 'yash'
        c.execute("""
            INSERT INTO users (username, password, role, class, paid_status) 
            VALUES ('yash', 'yash', 'student', 'Class 11', 'unpaid')
        """)
        conn.commit()
        
        print("✅ User 'yash' created successfully!")
        print(f"   Username: yash")
        print(f"   Password: yash")
        print(f"   Role: student")
        print(f"   Class: Class 11")
    
    conn.close()

if __name__ == "__main__":
    check_and_create_user()
