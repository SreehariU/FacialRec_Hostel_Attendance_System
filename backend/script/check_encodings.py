import pickle

MODEL_PATH = "backend/models/face_encodings.pkl"

with open(MODEL_PATH, "rb") as f:
    encodings = pickle.load(f)

print(f"Loaded encodings for {len(encodings)} students:")
for student_id, faces in encodings.items():
    print(f" - {student_id}: {len(faces)} encodings")
