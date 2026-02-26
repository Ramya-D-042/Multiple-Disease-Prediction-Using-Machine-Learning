import sqlite3
from werkzeug.security import generate_password_hash

# Connect to your database
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Insert a test user (replace with your email and password)
cur.execute("""
    INSERT OR IGNORE INTO users (username, email, phone, password)
    VALUES (?, ?, ?, ?)
""", ('testuser', 'upnischitha4@gmail.com', '0000000000', generate_password_hash('Test1234')))

cur.execute("""
    INSERT OR IGNORE INTO users (username, email, phone, password)
    VALUES (?, ?, ?, ?)
""", ('admin', 'dramya885@gmai.com', 'Admin@123', generate_password_hash('YourAdminPassword')))


conn.commit()
conn.close()
print("Email added to database (if it didn't exist).")
