import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import subprocess

app = Flask(__name__, template_folder='templates')

# MySQL Database connection
db = mysql.connector.connect(
    host="localhost",
    user="SreehariUpas",
    password="Sreehari@2005",
    database="attendance_system"
)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            if user['role'] == 'superadmin':
                return redirect(url_for('superadmin_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials, please try again."
    return render_template('admin_login.html')

# Superadmin Dashboard
@app.route('/superadmin_dashboard')
def superadmin_dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admins WHERE role='admin'")
    admins = cursor.fetchall()
    cursor.close()
    return render_template('superadmin_dashboard.html', admins=admins)

# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Combined route for registering students (GET to show form, POST to handle form submission)
@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        cursor = db.cursor()
        
        # Insert student into the database
        cursor.execute('INSERT INTO students (name, roll_no) VALUES (%s, %s)', (name, roll_no))
        db.commit()
        
        # Log the action
        cursor.execute("INSERT INTO admin_log (action) VALUES (%s)", (f"Registered student: {name}",))
        db.commit()
        
        cursor.close()
        return redirect(url_for('admin_dashboard'))
    
    # Render the registration form
    return render_template('register_student.html')


# Route to handle student registration (can be expanded to save to DB later)
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.form
    print("Student data received:", data)
    return "Student registered successfully!"

# Route to trigger Datacollection.py
def collect_face_data():
    face_name = request.form['face_name']

    if not face_name.strip():
        return jsonify({'status': 'error', 'message': 'Invalid name. Please enter a valid name for face data collection.'}), 400

    try:
        # Run Datacollection.py and pass the name
        process = subprocess.Popen(
            ['python3', 'backend/script/Datacollection.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=face_name)

        print("Datacollection.py output:", stdout)
        print("Datacollection.py errors:", stderr)

        if process.returncode == 0:
            return jsonify({'status': 'success', 'message': stdout.strip() or 'Face data collection started!'})
        else:
            return jsonify({'status': 'error', 'message': stderr.strip() or 'Unknown error occurred.'})

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({'status': 'error', 'message': str(e)})


# Room Assignment Page
@app.route('/assign_room', methods=['GET', 'POST'])
def assign_room():
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        room_no = request.form['room_no']
        cursor = db.cursor()
        cursor.execute('UPDATE students SET room_id = %s WHERE roll_no = %s', (room_no, roll_no))
        db.commit()
        cursor.execute("INSERT INTO admin_log (action) VALUES ('Assigned room {} to student {}')".format(room_no, roll_no))
        db.commit()
        cursor.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('assign_room.html')

# Billing Page
@app.route('/billing', methods=['GET', 'POST'])
def billing():
    if request.method == 'POST':
        roll_no = request.form['roll_no']
        rent_fee = request.form['rent_fee']
        mess_fee = request.form['mess_fee']
        cursor = db.cursor()
        cursor.execute('INSERT INTO billing (roll_no, rent, mess_fee) VALUES (%s, %s, %s)', (roll_no, rent_fee, mess_fee))
        db.commit()
        cursor.execute("INSERT INTO admin_log (action) VALUES ('Added billing for student {}')".format(roll_no))
        db.commit()
        cursor.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('billing.html')

# Admin Logs Page
@app.route('/admin_logs')
def admin_logs():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin_log ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    cursor.close()
    return render_template('admin_logs.html', logs=logs)

if __name__ == "__main__":
    app.run(debug=True)
