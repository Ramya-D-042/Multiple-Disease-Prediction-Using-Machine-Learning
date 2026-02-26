import sqlite3
from werkzeug.security import generate_password_hash

# Connect to your database
conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Set new admin email and password
new_email = "admin@example.com"  # choose your new admin email
new_password = "Admin12345"      # choose your new admin password

hashed_password = generate_password_hash(new_password)

# Check if admin exists
cur.execute("SELECT * FROM users WHERE username='admin'")
if cur.fetchone():
    # Update existing admin
    cur.execute("UPDATE users SET email=?, password=? WHERE username='admin'", (new_email, hashed_password))
else:
    # Create admin if not exists
    cur.execute("INSERT INTO users (username,email,phone,password) VALUES (?,?,?,?)",
                ('admin', new_email, '0000000000', hashed_password))

conn.commit()
conn.close()

print(f"Admin reset! Login with email: {new_email} and password: {new_password}")
