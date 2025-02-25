import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from flask import jsonify


app = Flask(__name__, template_folder='templates')

db = mysql.connector.connect(
    host="localhost",
    user="SreehariUpas",
    password="Sreehari@2005",
    database="attendance_system"
)

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/admin_dashboard')
def admin_dashboard():
    return "Admin Dashboard - Restricted to Admins"

@app.route('/superadmin_dashboard')
def superadmin_dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admins WHERE role='admin'")
    admins = cursor.fetchall()
    cursor.close()
    return render_template('superadmin_dashboard.html', admins=admins)

@app.route('/add_admin', methods=['POST'])
def add_admin():
    username = request.form['username']
    password = request.form['password']
    cursor = db.cursor()
    cursor.execute("INSERT INTO admins (username, password, role) VALUES (%s, %s, 'admin')", (username, password))
    db.commit()
    cursor.close()
    return redirect(url_for('superadmin_dashboard'))



@app.route('/remove_admin', methods=['POST'])
def remove_admin():
    username = request.form['username']
    cursor = db.cursor()
    cursor.execute("DELETE FROM admins WHERE username = %s", (username,))
    db.commit()
    cursor.close()
    return jsonify({'success': True})



if __name__ == "__main__":
    app.run(debug=True)
