import cv2
import face_recognition
import numpy as np
import pickle
import sys
import os

# Get the absolute path to the models folder
models_folder = os.path.join(os.path.dirname(__file__), "../models")
pkl_file = os.path.join(models_folder, "face_encodings.pkl")

# Load trained face encodings
try:
    with open(pkl_file, "rb") as f:
        data = pickle.load(f)
    
    encodings = np.array(data["encodings"])
    labels = np.array(data["labels"])
except FileNotFoundError:
    print(f"Error: {pkl_file} not found!")
    sys.exit(1)

# Ensure an image path is provided
if len(sys.argv) != 2:
    print("Usage: python3 face.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]

# Load the image
img = cv2.imread(image_path)
if img is None:
    print("Error: Could not load image at", image_path)
    sys.exit(1)

# Convert image to RGB for face recognition
rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# Detect faces and encode
face_locations = face_recognition.face_locations(rgb_img)
face_encodings = face_recognition.face_encodings(rgb_img, face_locations)

# Identify faces
recognized_student_id = "Unknown"

for face_encoding in face_encodings:
    face_distances = face_recognition.face_distance(encodings, face_encoding)
    match_index = np.argmin(face_distances)
    confidence = 1 - face_distances[match_index]

    if face_distances[match_index] < 0.5:  # Threshold for recognition
        recognized_student_id = labels[match_index]
        break

# Output the recognized student ID for Flask to capture
print(recognized_student_id)
