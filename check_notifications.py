import sqlite3 
conn = sqlite3.connect('users.db') 
c = conn.cursor() 
c.execute('SELECT id, message, class_id, target_paid_status, created_at FROM notifications ORDER BY id DESC LIMIT 5') 
print('Recent notifications:') 
for row in c.fetchall(): 
    print(row) 
conn.close() 
