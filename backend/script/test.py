import face_recognition
import os
import pickle

MODEL_PATH = "backend/models/face_encodings.pkl"
TEST_IMAGE_PATH = "backend/script/test_image.jpg"  # Updated to scripts folder

def verify_face():
    # Load the trained encodings
    if not os.path.exists(MODEL_PATH):
        print("❌ Model file not found. Train the model first!")
        return
    
    with open(MODEL_PATH, "rb") as f:
        encodings = pickle.load(f)

    # Load the test image
    if not os.path.exists(TEST_IMAGE_PATH):
        print("❌ Test image not found! Place a test image in 'backend/script/'.")
        return
    
    test_image = face_recognition.load_image_file(TEST_IMAGE_PATH)
    test_encodings = face_recognition.face_encodings(test_image)

    if len(test_encodings) == 0:
        print("⚠️ No faces found in the test image!")
        return
    
    test_encoding = test_encodings[0]  # Assume only one face in test image

    # Compare with stored encodings
    for student_id, known_encoding in encodings.items():
        match = face_recognition.compare_faces([known_encoding], test_encoding)[0]

        if match:
            print(f"✅ Face matches with Student ID: {student_id}")
            return

    print("❌ No match found.")

if __name__ == "__main__":
    verify_face()
