import sqlite3
from datetime import datetime

# ==============================================================================
# Database Initialization and Migration
# ==============================================================================

def init_db():
    init_classes_db()  # Ensure classes table is ready first
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # --- Schema Definitions ---
    # The 'role' and 'class_role' columns are kept temporarily for migration
    # and will be removed in a future step. New code will use class_id.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT, -- Deprecated, for migration
            paid TEXT NOT NULL DEFAULT 'not paid',
            class_id INTEGER REFERENCES classes(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            class_role TEXT, -- Deprecated, for migration
            filepath TEXT NOT NULL,
            title TEXT,
            description TEXT,
            class_id INTEGER REFERENCES classes(id),
            category TEXT NOT NULL DEFAULT 'uncategorized'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            class_role TEXT, -- Deprecated, for migration
            created_at TEXT NOT NULL,
            class_id INTEGER REFERENCES classes(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_notification_status (
            user_id INTEGER NOT NULL,
            notification_id INTEGER NOT NULL,
            seen_at TEXT NOT NULL,
            PRIMARY KEY (user_id, notification_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE CASCADE
        )
    ''')
    # This table is from a previous step, ensuring it's still created.
    c.execute('''
        CREATE TABLE IF NOT EXISTS live_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_code TEXT NOT NULL UNIQUE,
            pin TEXT NOT NULL,
            meeting_url TEXT NOT NULL,
            topic TEXT,
            description TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS forum_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            parent_id INTEGER,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(parent_id) REFERENCES forum_messages(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS live_class_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            live_class_id INTEGER NOT NULL,
            user_id INTEGER,
            username TEXT,
            message TEXT,
            media_url TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(live_class_id) REFERENCES live_classes(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()

    # --- Data Migration ---
    # Use PRAGMA user_version to ensure this migration runs only once.
    c.execute('PRAGMA user_version')
    db_version = c.fetchone()[0]

    if db_version < 1:
        # Migration V1: From text roles to class_id foreign keys
        try:
            # Add new class_id columns
            c.execute('ALTER TABLE users ADD COLUMN class_id INTEGER REFERENCES classes(id)')
            c.execute('ALTER TABLE resources ADD COLUMN class_id INTEGER REFERENCES classes(id)')
            c.execute('ALTER TABLE notifications ADD COLUMN class_id INTEGER REFERENCES classes(id)')

            # Populate the new columns from the old text-based roles
            c.execute('UPDATE users SET class_id = (SELECT id FROM classes WHERE classes.name = users.role)')
            c.execute('UPDATE resources SET class_id = (SELECT id FROM classes WHERE classes.name = resources.class_role)')
            c.execute('UPDATE notifications SET class_id = (SELECT id FROM classes WHERE classes.name = notifications.class_role)')
            
            # Set the new version
            c.execute('PRAGMA user_version = 1')
            conn.commit()
        except sqlite3.OperationalError as e:
            # This might happen if the script is interrupted. It's safe to ignore "duplicate column" errors.
            if "duplicate column" not in str(e):
                raise e
    
    if db_version < 2:
        # Migration V2: Add category to resources
        try:
            c.execute("ALTER TABLE resources ADD COLUMN category TEXT NOT NULL DEFAULT 'uncategorized'")
            c.execute('PRAGMA user_version = 2')
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e):
                raise e
    
    # --- Seed Admin User ---
    # Ensure the default admin user 'yash' exists.
    try:
        c.execute("SELECT id FROM classes WHERE name='admin'")
        admin_class_id = c.fetchone()[0]
        c.execute("SELECT id FROM users WHERE username='yash'")
        if c.fetchone() is None:
            # Admin user does not exist, create it.
            c.execute("INSERT INTO users (username, password, class_id, paid) VALUES (?, ?, ?, ?)",
                      ('yash', 'yash', admin_class_id, 'paid'))
            conn.commit()
    except (sqlite3.OperationalError, TypeError):
        # This might fail if tables are not ready, which is fine.
        # It will succeed on the next run.
        pass

    conn.close()
    # Note: init_resources_db and init_live_class_db are now integrated into init_db

def init_classes_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    # One-time population of the standard classes
    c.execute('SELECT COUNT(*) FROM classes')
    if c.fetchone()[0] == 0:
        classes_to_add = [
            'class 9', 'class 10 standard', 'class 10 basic',
            'class 11 applied', 'class 11 core', 'class 12 applied', 'class 12 core',
            'admin', 'teacher'
        ]
        c.executemany('INSERT INTO classes (name) VALUES (?)', [(c,) for c in classes_to_add])
    conn.commit()
    conn.close()

# ==============================================================================
# Helper Functions for Classes
# ==============================================================================

def get_all_classes():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM classes')
    classes = c.fetchall()
    conn.close()
    return classes

# ==============================================================================
# User Management Functions (Refactored)
# ==============================================================================

def register_user(username, password, class_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        # New registrations now use class_id directly
        c.execute('INSERT INTO users (username, password, class_id) VALUES (?, ?, ?)', (username, password, class_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT u.id, c.name FROM users u
        JOIN classes c ON u.class_id = c.id
        WHERE u.username=? AND u.password=?
    ''', (username, password))
    result = c.fetchone()
    conn.close()
    if result:
        return result  # (user_id, class_name)
    return None

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, c.name, u.paid FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
    ''')
    users = c.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, u.class_id, u.paid, c.name FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
        WHERE u.id=?
    ''', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user(user_id, username, class_id, paid):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET username=?, class_id=?, paid=? WHERE id=?', (username, class_id, paid, user_id))
    conn.commit()
    conn.close()

def search_users(query):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, c.name, u.paid FROM users u
        LEFT JOIN classes c ON u.class_id = c.id
        WHERE u.username LIKE ?
    ''', (f'%{query}%',))
    users = c.fetchall()
    conn.close()
    return users

# (delete_user remains the same as it uses id)

# ==============================================================================
# Resource Management Functions (Refactored)
# ==============================================================================

def save_resource(filename, class_id, filepath, title, description, category):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO resources (filename, class_id, filepath, title, description, category) VALUES (?, ?, ?, ?, ?, ?)', 
              (filename, class_id, filepath, title, description, category))
    conn.commit()
    conn.close()

def get_all_resources():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT r.filename, r.class_id, r.filepath, r.title, r.description, r.category FROM resources r
    ''')
    resources = c.fetchall()
    conn.close()
    return resources

def get_resources_for_class_id(class_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT r.filename, r.class_id, r.filepath, r.title, r.description, r.category FROM resources r
        WHERE r.class_id = ?
    ''', (class_id,))
    resources = c.fetchall()
    conn.close()
    return resources

# (delete_resource remains the same as it uses filename)

# ==============================================================================
# Notification Management Functions (Refactored)
# ==============================================================================

def add_notification(message, class_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO notifications (message, class_id, created_at) VALUES (?, ?, ?)', 
              (message, class_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_unread_notifications_for_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # First, get the class_id for the user
    c.execute('SELECT class_id FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    if not result:
        conn.close()
        return []
    class_id = result[0]

    # Now, get all notifications for that class that the user hasn't seen
    c.execute('''
        SELECT n.id, n.message, n.created_at
        FROM notifications n
        LEFT JOIN user_notification_status uns ON n.id = uns.notification_id AND uns.user_id = ?
        WHERE n.class_id = ? AND uns.notification_id IS NULL
        ORDER BY n.created_at DESC
    ''', (user_id, class_id))
    notifications = c.fetchall()
    conn.close()
    return notifications

def mark_notification_as_seen(user_id, notification_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO user_notification_status (user_id, notification_id, seen_at) VALUES (?, ?, ?)',
                  (user_id, notification_id, datetime.now().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        # This will fail if the primary key (user_id, notification_id) already exists, which is fine.
        # It means the notification was already marked as seen.
        pass
    finally:
        conn.close()

def get_notifications_for_class(class_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT message, created_at FROM notifications WHERE class_id=? ORDER BY created_at DESC', (class_id,))
    notifications = c.fetchall()
    conn.close()
    return notifications

def get_all_notifications():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT n.id, n.message, c.name, n.created_at FROM notifications n
        LEFT JOIN classes c ON n.class_id = c.id
        ORDER BY created_at DESC
    ''')
    notifications = c.fetchall()
    conn.close()
    return notifications

# ==============================================================================
# Live Class and Other Functions (Remain Unchanged)
# ==============================================================================

# ... (delete_user, delete_resource, live_class functions, etc. are here) ...
# Note: I have integrated the unchanged functions from the previous state of the file below.
def delete_resource(filename):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM resources WHERE filename=?', (filename,))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

def create_live_class(class_code, pin, meeting_url, topic, description):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO live_classes (class_code, pin, meeting_url, topic, description, created_at) VALUES (?, ?, ?, ?, ?, ?)',
              (class_code, pin, meeting_url, topic, description, datetime.now().isoformat()))
    conn.commit()
    new_class_id = c.lastrowid
    conn.close()
    return new_class_id

def get_live_class(class_code, pin):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT meeting_url FROM live_classes WHERE class_code=? AND pin=? AND is_active=1', (class_code, pin))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_active_classes():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT id, class_code, pin, topic, description, created_at FROM live_classes WHERE is_active=1 ORDER BY created_at DESC')
    classes = c.fetchall()
    conn.close()
    return classes

def get_class_details_by_id(class_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT class_code, pin, meeting_url, topic, description FROM live_classes WHERE id=?', (class_id,))
    details = c.fetchone()
    conn.close()
    return details

def deactivate_class(class_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE live_classes SET is_active=0 WHERE id=?', (class_id,))
    conn.commit()
    conn.close()

def delete_notification(notification_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM user_notification_status WHERE notification_id=?', (notification_id,))
    c.execute('DELETE FROM notifications WHERE id=?', (notification_id,))
    conn.commit()
    conn.close()

def save_forum_message(user_id, username, message, parent_id=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO forum_messages (user_id, username, message, parent_id) VALUES (?, ?, ?, ?)",
        (user_id, username, message, parent_id)
    )
    conn.commit()
    conn.close()

def get_forum_messages(parent_id=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if parent_id is None:
        c.execute("SELECT * FROM forum_messages WHERE parent_id IS NULL ORDER BY timestamp DESC")
    else:
        c.execute("SELECT * FROM forum_messages WHERE parent_id = ? ORDER BY timestamp ASC", (parent_id,))
    messages = c.fetchall()
    conn.close()
    return messages

def vote_on_message(message_id, vote_type):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    if vote_type == 'upvote':
        c.execute("UPDATE forum_messages SET upvotes = upvotes + 1 WHERE id = ?", (message_id,))
    elif vote_type == 'downvote':
        c.execute("UPDATE forum_messages SET downvotes = downvotes + 1 WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()

def delete_forum_message(message_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM forum_messages WHERE id = ? OR parent_id = ?", (message_id, message_id))
    conn.commit()
    conn.close()

def save_live_class_message(live_class_id, user_id, username, message, media_url=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO live_class_messages (live_class_id, user_id, username, message, media_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (live_class_id, user_id, username, message, media_url))
    conn.commit()
    conn.close()

def get_live_class_messages(live_class_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, user_id, username, message, media_url, timestamp
        FROM live_class_messages
        WHERE live_class_id = ?
        ORDER BY timestamp ASC
    ''', (live_class_id,))
    messages = c.fetchall()
    conn.close()
    return messages

def delete_live_class_message(message_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('DELETE FROM live_class_messages WHERE id = ?', (message_id,))
    conn.commit()
    conn.close()