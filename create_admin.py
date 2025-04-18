import mysql.connector
from werkzeug.security import generate_password_hash

# MySQL connection (update password if needed)
db = mysql.connector.connect(
    host="sql12.freesqldatabase.com",
    user="sql12772847",
    password="mr4xZhvxe5",
    database="sql12772847"
)

cursor = db.cursor()

# Admin credentials
username = "viggu"
password = "3228"
hashed_password = generate_password_hash(password)

# Insert admin into users table
try:
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                   (username, hashed_password, 'admin'))
    db.commit()
    print("Admin user 'viggu' created successfully!")
except Exception as e:
    print("Error:", e)

cursor.close()
db.close()
