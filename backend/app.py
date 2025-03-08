import os
import datetime
import subprocess
import logging
import numpy as np
import base64
import cv2
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import mysql.connector
from flask_cors import CORS

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)

# ✅ Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="backend/static")
CORS(app)

# ✅ Dataset directory
# ✅ Update the dataset directory to the correct path
DATASET_DIR = "/Users/sreehariupas/Desktop/Face_detection_attendance copy/backend/dataset"

if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)
UPLOAD_FOLDER = "backend/dataset"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Function to get a new MySQL connection
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="SreehariUpas",
            password="Sreehari@2005",
            database="attendance_system",
            autocommit=True
        )
    except mysql.connector.Error as e:
        print("🔥 Database Connection Error:", e)
        return None

# ✅ Home route
@app.route("/")
def home():
    return render_template("index.html")

# ✅ Save face images directly to the dataset folder
@app.route('/save_face_image', methods=['POST'])
def save_face_image():
    try:
        data = request.json
        student_name = data['name'].replace(' ', '_')
        image_data = data['image'].split(",")[1]

        student_dir = os.path.join(DATASET_DIR, student_name)
        os.makedirs(student_dir, exist_ok=True)

        image_count = len(os.listdir(student_dir)) + 1
        image_path = os.path.join(student_dir, f"{student_name}_{image_count}.jpg")

        with open(image_path, "wb") as img_file:
            img_file.write(base64.b64decode(image_data))

        logging.debug(f"✅ Image saved at: {image_path}")
        return jsonify({"message": "Image saved", "path": image_path})

    except Exception as e:
        logging.error(f"❌ Error saving image: {e}")
        return jsonify({"error": "Failed to save image"}), 500
# ✅ Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if user["role"] == "superadmin":
                return redirect(url_for("superadmin_dashboard"))
            else:
                return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid credentials, please try again."
    return render_template("admin_login.html")

# ✅ Superadmin dashboard
@app.route("/superadmin_dashboard")
def superadmin_dashboard():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admins WHERE role='admin'")
    admins = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template("superadmin_dashboard.html", admins=admins)

# ✅ Admin dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

# ✅ Get the next student ID
def get_next_id():
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM students")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        next_id = (result[0] + 1) if result[0] else 1
        return next_id
    except mysql.connector.Error as e:
        print("🔥 Database Error:", e)
        return None

@app.route("/get_next_student_id", methods=["GET"])
def get_next_student_id():
    next_id = get_next_id()
    if next_id is None:
        return jsonify({"error": "Database connection failed"}), 500
    return jsonify({"next_id": next_id})

# ✅ Register student route
# ✅ Register student route
@app.route("/register_student", methods=["GET", "POST"])
def register_student():
    if request.method == "GET":
        return render_template("register_student.html")

    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        name = data.get("name")
        roll_no = data.get("roll_no")
        room_id = int(data.get("room_id", 0))
        contact_number = data.get("contact_number")
        parents_number = data.get("parents_number")
        email = data.get("email")
        emergency_contact = data.get("emergency_contact")
        semester = data.get("semester", "")  # ✅ Corrected!
        year = int(data.get("year", 0))
        stream = data.get("stream")
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()

        sql = """
        INSERT INTO students (name, roll_no, room_id, contact_number, parents_number, email, 
        emergency_contact, semester, year, stream, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (name, roll_no, room_id, contact_number, parents_number, email, emergency_contact, semester, year, stream, created_at)

        try:
            cursor.execute(sql, values)
            conn.commit()
            student_id = cursor.lastrowid

            # ✅ Run Datacollection.py — fixed file path
            student_name = name.replace(' ', '_')
            datacollection_cmd = ["python3", "script/Datacollection.py", student_name]
            subprocess.run(datacollection_cmd, check=True)
            logging.debug(f"✅ Datacollection.py executed for {student_name}")

            # ✅ Run train.py — fixed file path
            train_cmd = ["python3", "script/train.py"]
            subprocess.run(train_cmd, check=True)
            logging.debug("✅ train.py executed successfully")

            return jsonify({"message": "Student registered, face data collected, and model trained!"}), 201

        except FileNotFoundError as e:
            conn.rollback()
            logging.error(f"❌ Script file not found: {e}")
            return jsonify({"error": "Required script not found"}), 500

        except subprocess.CalledProcessError as e:
            conn.rollback()
            logging.error(f"❌ Error running scripts: {e}")
            return jsonify({"error": "Failed to process face data or train model"}), 500

        except mysql.connector.Error as err:
            conn.rollback()
            logging.error(f"❌ Database Error: {err}")
            return jsonify({"error": f"Database error: {err}"}), 500

        finally:
            cursor.close()
            conn.close()


# ✅ Serve model files
@app.route("/models/<path:filename>")
def serve_models(filename):
    return send_from_directory("backend/models", filename)

if __name__ == "__main__":
    app.run(debug=True)
