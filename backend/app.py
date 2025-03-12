import os
from datetime import datetime
import pickle
import subprocess
import logging
import face_recognition

import numpy as np
import requests
import json
import base64
import cv2
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask import Flask, render_template, jsonify, send_from_directory, redirect, url_for, flash, session
from supabase import Client, create_client


# ✅ Supabase config
SUPABASE_URL = "https://ikrjvtpgoteoimpkxfvy.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlrcmp2dHBnb3Rlb2ltcGt4ZnZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDE2NzY1MzgsImV4cCI6MjA1NzI1MjUzOH0.ihRg2JjYwOQHZN__BqBS7sbItObKvh4Yehb3gZL9B6o"
SUPABASE_HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

supabase = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# ✅ Temporary folder for storing captured images
TEMP_IMAGE_FOLDER = "backend/temp_images"
MODEL_PATH = "backend/models/face_encodings.pkl"
os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)
# Define a valid temp image folder
TEMP_IMAGE_FOLDER = "/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/temp_images"

# Ensure the folder exists
os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)

if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        known_encodings = pickle.load(f)
else:
    known_encodings = {}

# ✅ Setup logging
logging.basicConfig(level=logging.DEBUG)

# ✅ Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="backend/static")
CORS(app)
app.secret_key = 'your_super_secret_key'

# ✅ Dataset directory
DATASET_DIR = "/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

UPLOAD_FOLDER = "backend/dataset"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Delete student from Supabase
@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    try:
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/students?id=eq.{student_id}",
            headers=SUPABASE_HEADERS
        )
        
        if response.status_code == 204:
            logging.info(f"✅ Student with ID {student_id} deleted.")
            return jsonify({"message": "Student deleted successfully"}), 200
        else:
            logging.error(f"❌ Failed to delete student: {response.text}")
            return jsonify({"error": "Failed to delete student"}), 500

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        return jsonify({"error": "An error occurred"}), 500

# ✅ Home route
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/save_face_image', methods=['POST'])
def save_face_image():
    try:
        data = request.json
        student_id = data.get('student_id')
        image_data = data.get('image')

        if not student_id or not image_data:
            logging.error("❌ Missing student_id or image data.")
            return jsonify({"error": "Missing student_id or image data"}), 400

        # Create a folder using student_id
        student_dir = os.path.join(DATASET_DIR, student_id)
        os.makedirs(student_dir, exist_ok=True)

        # Save images sequentially
        image_count = len([f for f in os.listdir(student_dir) if f.endswith(".jpg")]) + 1
        image_path = os.path.join(student_dir, f"face_{image_count}.jpg")

        # Save the image
        with open(image_path, "wb") as img_file:
            img_file.write(base64.b64decode(image_data.split(",")[1]))

        logging.debug(f"✅ Image saved at: {image_path}")
        return jsonify({"message": "Image saved", "path": image_path})

    except Exception as e:
        logging.error(f"❌ Error saving image: {e}")
        return jsonify({"error": "Failed to save image"}), 500


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # or however you handle logout
    return redirect(url_for('home'))

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('admin_login.html')

    data = request.form
    username = data.get('username')
    password = data.get('password')

    try:
        # Query the Supabase 'admins' table to check credentials
        response = supabase.table('admins').select('username, role').eq('username', username).eq('password', password).execute()
        user = response.data[0] if response.data else None
        
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'superadmin':
                return redirect(url_for('superadmin_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid username or password")

    except Exception as e:
        print(f"Error during login: {e}")
        return render_template('admin_login.html', error="An error occurred during login")



# ✅ Record attendance (insert into StudentCheckins table)
def record_attendance(student_id):
    try:
        payload = {
            "StudentID": student_id,
            "CheckinDate": "NOW()",
            "CheckinTime": "NOW()"
        }
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/StudentCheckins",
            headers=SUPABASE_HEADERS,
            json=payload
        )

        if response.status_code == 201:
            print(f"✅ Attendance recorded for StudentID: {student_id}")
        else:
            print(f"❌ Failed to record attendance: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

# ✅ Superadmin dashboard
@app.route("/superadmin_dashboard")
def superadmin_dashboard():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/admins?role=eq.admin",
            headers=SUPABASE_HEADERS
        )
        admins = response.json()
        return render_template("superadmin_dashboard.html", admins=admins)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Add new admin
@app.route('/add_admin', methods=['POST'])
def add_admin():
    try:
        data = request.form
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required"}), 400

        # Check if username already exists
        response = supabase.table('admins').select('username').eq('username', username).execute()
        if response.data:  # Check if username already exists
            return jsonify({"success": False, "message": "Username already exists"}), 400

        # Insert new admin with role 'admin'
        supabase.table('admins').insert({
            "username": username,
            "password": password,
            "role": "admin"
        }).execute()

        # Redirect back to superadmin dashboard after adding admin
        return redirect(url_for('superadmin_dashboard'))

    except Exception as e:
        print("Error adding admin:", str(e))
        return jsonify({"success": False, "message": "Internal server error"}), 500


# ✅ Remove an admin
@app.route('/remove_admin', methods=['POST'])
def remove_admin():
    username = request.form['username']

    # Delete admin from Supabase
    response = supabase.table('admins').delete().eq('username', username).execute()

    if response.data:
        return jsonify({"success": True, "message": "Admin removed successfully!"})
    else:
        return jsonify({"success": False, "message": "Failed to remove admin."}), 500

# ✅ Admin dashboard
@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")






TEMP_IMAGE_FOLDER = "/path/to/temp/images"  # Update this if necessary
FACE_ENCODINGS_PATH = "/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/face_encodings.pkl"

# Load known face encodings from the pickle file
known_encodings = {}

def load_face_encodings():
    global known_encodings
    try:
        with open(FACE_ENCODINGS_PATH, 'rb') as f:
            known_encodings = pickle.load(f)
        print("✅ Loaded known face encodings.")
    except FileNotFoundError:
        print("⚠️ face_encodings.pkl not found. Please train the model first.")
        known_encodings = {}
    except Exception as e:
        print(f"❌ Error loading face encodings: {e}")
        known_encodings = {}

# Initial model loading
load_face_encodings()

# ✅ Process attendance (Supabase integration)
TEMP_IMAGE_FOLDER = "/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/temp_images"

@app.route('/process_attendance', methods=['POST'])
def process_attendance():
    try:
        # Ensure the temp image folder exists
        if not os.path.exists(TEMP_IMAGE_FOLDER):
            os.makedirs(TEMP_IMAGE_FOLDER)

        data = request.json
        if not data or 'image' not in data:
            return jsonify({"success": False, "message": "No image data received"}), 400

        # Decode and save the image
        image_data = base64.b64decode(data['image'].split(",")[1])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(TEMP_IMAGE_FOLDER, f"capture_{timestamp}.jpg")

        with open(image_path, "wb") as f:
            f.write(image_data)

        # Load and process the image
        test_image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(test_image)

        if not face_encodings:
            os.remove(image_path)
            return jsonify({"success": False, "message": "No faces detected"}), 200

        test_encoding = face_encodings[0]
        recognized_student_id = "Unknown"

        # Compare encodings
        for student_id, student_encodings in known_encodings.items():
            if any(face_recognition.compare_faces([enc], test_encoding)[0] for enc in student_encodings):
                recognized_student_id = student_id
                break

        # Record attendance in Supabase if recognized
        if recognized_student_id != "Unknown":
            attendance_data = {
                "student_id": recognized_student_id,
                "checkin_date": datetime.now().strftime("%Y-%m-%d"),
                "checkin_time": datetime.now().strftime("%H:%M:%S")
            }

            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/attendance",
                headers=SUPABASE_HEADERS,
                json=attendance_data
            )

            if response.status_code != 201:
                logging.error(f"❌ Failed to record attendance: {response.text}")
                return jsonify({"success": False, "message": "Failed to record attendance"}), 500

        # Remove the temp image after processing
        os.remove(image_path)

        return jsonify({
            "success": True,
            "student_id": recognized_student_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S")
        })

    except Exception as e:
        logging.error(f"❌ Error processing attendance: {str(e)}")
        return jsonify({"success": False, "message": "Internal server error"}), 500


# ✅ Render attendance page
@app.route('/attendance')
def attendance():
    return render_template('attendance.html')

# ✅ Edit student details (GET + POST)
@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    try:
        # Fetch student data from Supabase
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/students?id=eq.{student_id}",
            headers=SUPABASE_HEADERS
        )

        if response.status_code != 200 or not response.json():
            return "Student not found", 404

        student = response.json()[0]

        if request.method == 'POST':
            # Update student data in Supabase
            update_data = {key: request.form[key] for key in request.form}

            update_response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/students?id=eq.{student_id}",
                headers=SUPABASE_HEADERS,
                json=update_data
            )

            if update_response.status_code != 204:
                flash("Failed to update student", "error")
            else:
                flash("Student updated successfully!", "success")
            return redirect(url_for('manage_students'))

        return render_template('edit_student.html', student=student)

    except Exception as e:
        logging.error(f"❌ Error editing student: {str(e)}")
        return "Internal server error", 500
    
@app.route('/get_next_student_id')
def get_next_student_id():
    try:
        response = supabase.table('students').select('id').order('id', desc=True).limit(1).execute()
        print("Supabase response:", response)  # Log the full response
        if response.data:
            last_id = response.data[0]['id']
            next_id = last_id + 1
        else:
            next_id = 1
        return jsonify({"next_id": next_id})
    except Exception as e:
        print("Error fetching next student ID:", e)
        return jsonify({"error": "Failed to fetch next student ID"}), 500


# ✅ Update student details (POST)
@app.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    try:
        student_data = {
            "name": request.form['name'],
            "roll_no": request.form['roll_no'],
            "room_id": request.form['room_id'],
            "contact_number": request.form['contact_number'],
            "parents_number": request.form['parents_number'],
            "email": request.form['email'],
            "emergency_contact": request.form['emergency_contact'],
            "semester": request.form['semester'],
            "year": request.form['year'],
            "stream": request.form['stream']
        }

        # Update student in Supabase
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/students?id=eq.{student_id}",
            headers=SUPABASE_HEADERS,
            json=student_data
        )

        if response.status_code != 204:
            flash("Failed to update student", "error")
        else:
            flash("Student updated successfully!", "success")

        return redirect(url_for('manage_students'))

    except Exception as e:
        logging.error(f"❌ Error updating student: {str(e)}")
        return "Internal server error", 500




# ✅ Serve model files
@app.route("/models/<path:filename>")
def serve_models(filename):
    return send_from_directory("backend/models", filename)

@app.route('/attendance_log')
def attendance_log():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/attendance?select=student_id,students(name),checkin_date,checkin_time",
            headers=SUPABASE_HEADERS
        )

        print("Supabase response:", response.json())  # Log the full response

        if response.status_code != 200:
            logging.error(f"❌ Failed to fetch attendance logs: {response.text}")
            return jsonify({"error": "Failed to fetch attendance logs"}), 500

        attendance_logs = response.json()
        return render_template('attendance_log.html', attendance_logs=attendance_logs)

    except Exception as e:
        logging.error(f"❌ Error fetching attendance logs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500



# ✅ Manage students route (Supabase integration)
@app.route('/manage_students')
def manage_students():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/students?select=*&order=created_at.desc",
            headers=SUPABASE_HEADERS
        )

        if response.status_code != 200:
            logging.error(f"❌ Failed to fetch students: {response.text}")
            return jsonify({"error": "Failed to fetch students"}), 500

        students = response.json()

        return render_template('manage_students.html', students=students)

    except Exception as e:
        logging.error(f"❌ Error fetching students: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ✅ Register student route
@app.route("/register_student", methods=["GET", "POST"])
def register_student():
    if request.method == "GET":
        return render_template("register_student.html")

    try:
        # ✅ Handle both JSON and form data
        data = request.get_json() if request.is_json else request.form

        # ✅ Validate required fields
        required_fields = ["name", "roll_no", "room_id", "contact_number", "email"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            logging.error(f"❌ Missing fields: {missing_fields}")
            return jsonify({"error": f"Missing fields: {missing_fields}"}), 400

        # ✅ Collect student data
        student_payload = {
            "name": data.get("name").strip(),
            "roll_no": data.get("roll_no").strip(),
            "room_id": int(data.get("room_id", 0)),
            "contact_number": data.get("contact_number").strip(),
            "parents_number": data.get("parents_number", "").strip(),
            "email": data.get("email").strip(),
            "emergency_contact": data.get("emergency_contact", "").strip(),
            "semester": data.get("semester", "").strip(),
            "year": int(data.get("year", 0)),
            "stream": data.get("stream", "").strip(),
            "created_at": datetime.now().isoformat()
        }

        logging.debug(f"📦 Student data to be inserted: {student_payload}")

        # ✅ Insert student into Supabase (returning the new student’s ID)
        SUPABASE_HEADERS["Prefer"] = "return=representation"
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/students",
            headers=SUPABASE_HEADERS,
            json=student_payload
        )

        if response.status_code != 201:
            logging.error(f"❌ Failed to insert into Supabase: {response.text}")
            return jsonify({"error": "Failed to register student"}), 500

        # ✅ Get inserted student ID
        student_data = response.json()
        if not student_data or not isinstance(student_data, list) or not student_data[0].get("id"):
            logging.error("❌ Student ID not found in response.")
            return jsonify({"error": "Failed to get student ID"}), 500

        student_id = str(student_data[0]["id"])
        logging.debug(f"✅ Student registered with ID: {student_id}")

        # ✅ Hardcoded path to process_and_train.py
        process_and_train_path = "/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/script/process_and_train.py"
        if not os.path.exists(process_and_train_path):
            logging.error(f"❌ process_and_train.py not found at {process_and_train_path}")
            return jsonify({"error": "Face processing script missing"}), 500

        # Execute process_and_train.py with student_id as argument
        try:
            result = subprocess.run(
                ["python3", process_and_train_path, student_id],
                check=True,
                capture_output=True,
                text=True
            )
            logging.debug(f"✅ process_and_train.py output: {result.stdout}")

        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Error running process_and_train.py: {e.stderr}")
            return jsonify({"error": "Face processing and model training failed"}), 500

        return jsonify({"message": "Student registered, face data collected, and model trained!"}), 201

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Supabase request error: {e}")
        return jsonify({"error": "Database error"}), 500

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Error running script: {e}")
        return jsonify({"error": "Script execution failed"}), 500

    except ValueError as e:
        logging.error(f"❌ Invalid data type: {e}")
        return jsonify({"error": "Invalid data format"}), 400

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return jsonify({"error": "Unexpected error occurred"}), 500



if __name__ == "__main__":
    app.run(debug=True)
