import pickle
import os

# Path to the face encodings file
ENCODINGS_FILE = "/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/face_encodings.pkl"

def load_encodings():
    if not os.path.exists(ENCODINGS_FILE):
        print(f"[ERROR] Encodings file not found at {ENCODINGS_FILE}")
        return None
    
    try:
        with open(ENCODINGS_FILE, "rb") as file:
            encodings = pickle.load(file)
            return encodings
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        print(f"[ERROR] Failed to load encodings: {e}")
        return None

def check_encodings():
    encodings = load_encodings()
    if encodings is None:
        print("[INFO] No encodings found.")
        return

    print(f"[INFO] Loaded encodings for {len(encodings)} student(s):\n")

    for student_id, faces in encodings.items():
        print(f"Student ID: {student_id}")
        print(f"Number of face encodings: {len(faces)}")
        # Uncomment the next line to print the actual encodings (optional)
        # print(f"Encodings: {faces}\n")
        print("-" * 40)

if __name__ == "__main__":
    check_encodings()
