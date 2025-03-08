import os
import pickle
import face_recognition

DATASET_PATH = "backend/dataset"
MODEL_PATH = "backend/models/face_encodings.pkl"
VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")  # Only process images

def train_model():
    encodings = {}

    for student_id in os.listdir(DATASET_PATH):
        student_folder = os.path.join(DATASET_PATH, student_id, "processed")

        if not os.path.exists(student_folder):
            print(f"⚠️ No processed images found for student {student_id}, skipping...")
            continue

        for img_name in os.listdir(student_folder):
            img_path = os.path.join(student_folder, img_name)

            # ✅ Ignore system files like .DS_Store
            if not img_name.lower().endswith(VALID_IMAGE_EXTENSIONS):
                print(f"⚠️ Skipping non-image file: {img_name}")
                continue

            try:
                img = face_recognition.load_image_file(img_path)

                # Get face encodings
                face_encodings = face_recognition.face_encodings(img)
                if face_encodings:  # ✅ Only store encoding if a face is found
                    encodings[student_id] = face_encodings[0]
                else:
                    print(f"⚠️ No face detected in {img_path}, skipping...")
            except Exception as e:
                print(f"⚠️ Error processing {img_path}: {e}")

    # Save encodings if at least one was found
    if encodings:
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(encodings, f)
        print("✅ Model training complete!")
    else:
        print("⚠️ No face encodings found. Model training skipped.")

if __name__ == "__main__":
    train_model()
