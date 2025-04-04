import cv2
import os
import sys
import numpy as np
import face_recognition
import pickle

# Path configuration
DATASET_DIR = '/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/dataset'
ENCODINGS_FILE = '/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/face_encodings.pkl'

print(f"[DEBUG] Dataset directory: {DATASET_DIR}")
print(f"[DEBUG] Encodings file: {ENCODINGS_FILE}")
print(f"[DEBUG] Current working directory: {os.getcwd()}")

# Process face images for the given student ID
def process_faces(student_id):
    student_dir = os.path.join(DATASET_DIR, str(student_id))
    processed_dir = os.path.join(student_dir, 'processed')

    print(f"[DEBUG] Looking for student directory: {student_dir}")
    print(f"[DEBUG] Processed directory: {processed_dir}")

    if not os.path.exists(student_dir):
        print(f"[ERROR] Student directory '{student_dir}' does not exist.")
        print(f"[DEBUG] Available student directories: {os.listdir(DATASET_DIR)}")
        return False

    os.makedirs(processed_dir, exist_ok=True)

    face_count = 0
    for file in os.listdir(student_dir):
        print(f"[DEBUG] Checking file: {file}")
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(student_dir, file)
            print(f"[DEBUG] Processing image: {img_path}")
            image = cv2.imread(img_path)
            if image is None:
                print(f"[WARNING] Could not read image '{img_path}'. Skipping.")
                continue

            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)

            for face_location in face_locations:
                top, right, bottom, left = face_location
                face_image = rgb_image[top:bottom, left:right]
                resized_face = cv2.resize(face_image, (150, 150))
                output_path = os.path.join(processed_dir, f'face_{face_count}.jpg')
                cv2.imwrite(output_path, cv2.cvtColor(resized_face, cv2.COLOR_RGB2BGR))
                print(f"[DEBUG] Saved processed face to: {output_path}")
                face_count += 1

    print(f"[INFO] Processed {face_count} faces for student ID: {student_id}.")
    return face_count > 0

# Train the model using processed face encodings
def train_model(student_id):
    processed_dir = os.path.join(DATASET_DIR, student_id, 'processed')
    print(f"[DEBUG] Looking for processed directory: {processed_dir}")

    if not os.path.exists(processed_dir):
        print(f"[ERROR] Processed data for student ID '{student_id}' not found.")
        return False

    # Load or initialize encodings
    try:
        with open(ENCODINGS_FILE, 'rb') as f:
            encodings = pickle.load(f)
        print(f"[DEBUG] Loaded existing encodings.")
    except (FileNotFoundError, EOFError):
        encodings = {}
        print(f"[DEBUG] No existing encodings found. Creating a new dictionary.")

    # Collect new face encodings
    known_encodings = []
    for file in os.listdir(processed_dir):
        img_path = os.path.join(processed_dir, file)
        print(f"[DEBUG] Processing encoding for: {img_path}")
        image = cv2.imread(img_path)
        if image is None:
            print(f"[WARNING] Could not read processed image '{img_path}'. Skipping.")
            continue

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_image)

        if face_encodings:
            known_encodings.append(face_encodings[0])

    if known_encodings:
        encodings[student_id] = known_encodings
        with open(ENCODINGS_FILE, 'wb') as f:
            pickle.dump(encodings, f)
        print(f"[INFO] Updated model with encodings for student ID: {student_id}.")
        return True
    else:
        print(f"[WARNING] No encodings found for student ID: {student_id}.")
        return False

# Main process
def main(student_id):
    if process_faces(student_id):
        if train_model(student_id):
            print("[SUCCESS] Face processing and model training completed.")
        else:
            print("[ERROR] Model training failed.")
    else:
        print("[ERROR] Face processing failed.")

# Entry point
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_and_train.py <student_id>")
        sys.exit(1)

    student_id = sys.argv[1]
    main(student_id)
