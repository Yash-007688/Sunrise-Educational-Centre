#!/usr/bin/env python3
import sqlite3
import os

def check_admission_setup():
    """Check if admission registration setup is correct"""
    
    print("🔍 Checking Admission Registration Setup...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Check if admissions table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admissions'")
        if c.fetchone():
            print('✅ admissions table exists')
            c.execute('PRAGMA table_info(admissions)')
            columns = c.fetchall()
            print('Columns in admissions table:')
            for col in columns:
                print(f'  {col[1]} ({col[2]})')
        else:
            print('❌ admissions table does not exist')
            return False
        
        print()
        
        # Check if admission_access table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admission_access'")
        if c.fetchone():
            print('✅ admission_access table exists')
        else:
            print('❌ admission_access table does not exist')
        
        # Check if admission_access_plain table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admission_access_plain'")
        if c.fetchone():
            print('✅ admission_access_plain table exists')
        else:
            print('❌ admission_access_plain table does not exist')
        
        print()
        
        # Check if uploads directory exists
        if os.path.exists('uploads/admission_photos'):
            print('✅ uploads/admission_photos directory exists')
        else:
            print('❌ uploads/admission_photos directory does not exist')
            print('Creating directory...')
            os.makedirs('uploads/admission_photos', exist_ok=True)
            print('✅ Directory created')
        
        print()
        
        # Test a sample admission insertion (rollback after test)
        print("🧪 Testing admission insertion...")
        try:
            c.execute('BEGIN TRANSACTION')
            c.execute('''INSERT INTO admissions (
                student_name, dob, student_phone, student_email, class, school_name,
                maths_marks, maths_rating, last_percentage, parent_name, parent_phone, 
                passport_photo, status, submitted_at, user_id, submit_ip
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                'Test Student',
                '2000-01-01',
                '1234567890',
                'test@example.com',
                'class 10',
                'Test School',
                75,
                8,
                85.5,
                'Test Parent',
                '0987654321',
                'test_photo.jpg',
                'pending',
                '2024-01-01 12:00:00',
                None,
                '127.0.0.1'
            ))
            print('✅ Test insertion successful')
            c.execute('ROLLBACK')  # Don't actually save the test data
        except Exception as e:
            print(f'❌ Test insertion failed: {e}')
            c.execute('ROLLBACK')
            return False
        
        conn.close()
        print("\n🎉 Admission registration setup appears to be working correctly!")
        return True
        
    except Exception as e:
        print(f'❌ Database error: {e}')
        return False

if __name__ == '__main__':
    check_admission_setup()
