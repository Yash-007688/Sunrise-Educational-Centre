import sqlite3
import os

def migrate_live_class_tables():
    """Add Daily.co related columns to live classes tables"""
    try:
        # Connect to database
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # Add room_url column to live_classes if it doesn't exist
        c.execute('''
            SELECT COUNT(*) FROM pragma_table_info('live_classes') 
            WHERE name='room_url'
        ''')
        if c.fetchone()[0] == 0:
            c.execute('''
                ALTER TABLE live_classes 
                ADD COLUMN room_url TEXT
            ''')

        # Add recording_url column if it doesn't exist
        c.execute('''
            SELECT COUNT(*) FROM pragma_table_info('live_classes') 
            WHERE name='recording_url'
        ''')
        if c.fetchone()[0] == 0:
            c.execute('''
                ALTER TABLE live_classes 
                ADD COLUMN recording_url TEXT
            ''')

        # Create class_attendance table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS class_attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                leave_time TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES live_classes(id),
                FOREIGN KEY (student_id) REFERENCES users(id)
            )
        ''')

        # Create indexes for performance
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_class_attendance_class_id 
            ON class_attendance(class_id)
        ''')
        c.execute('''
            CREATE INDEX IF NOT EXISTS idx_class_attendance_student_id 
            ON class_attendance(student_id)
        ''')

        # Commit changes
        conn.commit()
        print("Successfully updated database schema for Daily.co integration")

    except Exception as e:
        print(f"Error updating database schema: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_live_class_tables()