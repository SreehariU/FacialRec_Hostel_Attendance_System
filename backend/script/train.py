import os
import pickle
import face_recognition

# Paths
DATASET_PATH = "backend/dataset"
MODEL_PATH = "backend/models/face_encodings.pkl"
VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")  # Only process image files

def train_model():
    encodings = {}

    # Iterate through student folders in dataset
    for student_id in os.listdir(DATASET_PATH):
        if student_id.startswith('.'):  # Skip hidden files like .DS_Store
            continue
        print(f"📦 Processing folder for student ID: {student_id}")
        student_folder = os.path.join(DATASET_PATH, student_id, "processed")

        if not os.path.exists(student_folder):
            print(f"⚠️ No processed images found for student '{student_id}', skipping...")
            continue

        encodings[student_id] = []  # Prepare list for multiple face encodings

        # Process each image in the student's folder
        for img_name in os.listdir(student_folder):
            img_path = os.path.join(student_folder, img_name)

            if not img_name.lower().endswith(VALID_IMAGE_EXTENSIONS):
                print(f"⚠️ Skipping non-image file: {img_name}")
                continue

            try:
                img = face_recognition.load_image_file(img_path)
                face_encodings = face_recognition.face_encodings(img)

                if face_encodings:
                    encodings[student_id].append(face_encodings[0])
                else:
                    print(f"⚠️ No face detected in {img_name}, skipping...")

            except Exception as e:
                print(f"⚠️ Error processing {img_name}: {e}")

        # Remove student if no encodings were found
        if not encodings[student_id]:
            del encodings[student_id]
            print(f"⚠️ No valid encodings for '{student_id}', removed from model.")

    # Save encodings to file
    if encodings:
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(encodings, f)
        print(f"✅ Model training complete! Encodings saved for {len(encodings)} students.")
        for student, faces in encodings.items():
            print(f" - {student}: {len(faces)} encodings")
    else:
        print("⚠️ No face encodings found. Model training skipped.")

if __name__ == "__main__":
    train_model()
