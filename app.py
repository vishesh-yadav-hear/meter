
from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = '3228'
app.permanent_session_lifetime = timedelta(minutes=30)

# MySQL Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="viggu3228",
    database="meter_reading"
)
cursor = db.cursor(dictionary=True)

# ----- ROUTES -----

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect('/dashboard')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    if session['role'] == 'admin':
        # Admin Dashboard logic can go here
        return render_template('admin_dashboard.html', username=session['username'])

    elif session['role'] == 'user':
        return render_template('user_dashboard.html', username=session['username'])

    return "Unauthorized Access"

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session['role'] != 'admin':
        return redirect('/login')

    # Get total users
    cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE role = 'user'")
    total_users = cursor.fetchone()['total_users']

    # Get total readings
    cursor.execute("SELECT COUNT(*) AS total_readings FROM readings")
    total_readings = cursor.fetchone()['total_readings']

    return render_template('admin_dashboard.html', username=session['username'],
                           total_users=total_users, total_readings=total_readings)


@app.route('/register', methods=['POST'])
def register():
    if 'username' not in session or session['role'] != 'admin':
        return "Access Denied"

    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        return "Username already exists"

    hashed_pw = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                   (username, hashed_pw, role))
    db.commit()
    return "User registered successfully!"

@app.route('/save_reading', methods=['POST'])
def save_reading():
    if 'username' not in session or session['role'] != 'user':
        return redirect('/login')

    username = session['username']
    meter_number = request.form['meter_number']

    # Loop through readings
    for i in range(1, 7):
        reading1 = request.form.get(f'reading1_{i}')
        reading2 = request.form.get(f'reading2_{i}')

        cursor.execute("""
            INSERT INTO readings (username, meter_number, image_number, reading1, reading2)
            VALUES ( %s,%s, %s, %s, %s)
        """, (username, meter_number, i, reading1, reading2))

    db.commit()
    return "Readings saved successfully!"

# ----- RUN -----
if __name__ == '__main__':
    app.run(debug=True)

