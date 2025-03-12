import os
import pickle

# Path to the face encodings file
MODEL_PATH = "/Users/sreehariupas/Desktop/Face_detection_attendance copy 2/backend/models/face_encodings.pkl"

def clear_encodings():
    """
    Clears all face encodings by resetting the face_encodings.pkl file.
    """
    # Empty structure for encodings
    empty_data = {
        "encodings": [],
        "labels": [],
        "label_dict": {}
    }

    # Save the empty data to the pickle file
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(empty_data, f)

    print(f"✅ All face encodings cleared. {MODEL_PATH} has been reset.")

# Main execution
if __name__ == "__main__":
    if os.path.exists(MODEL_PATH):
        clear_encodings()
    else:
        print(f"❌ Error: File not found at {MODEL_PATH}")
