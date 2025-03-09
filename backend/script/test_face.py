import face_recognition
import cv2
import pickle
import os

# Load known face encodings
encodings_file = '/Users/sreehariupas/Desktop/Face_detection_attendance copy/backend/models/face_encodings.pkl'

if not os.path.exists(encodings_file):
    print(f"Error: {encodings_file} not found. Please train the model first.")
    exit()

with open(encodings_file, 'rb') as f:
    known_encodings = pickle.load(f)

print(f"Loaded face encodings for {len(known_encodings)} student(s).")

# Open webcam
video_capture = cv2.VideoCapture(0)
print("Press 'q' to capture an image...")

frame = None
while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to capture image.")
        break

    cv2.imshow('Face Detection Test', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()

if frame is None:
    print("No frame captured from webcam.")
    exit()

# Convert BGR (OpenCV) to RGB (face_recognition)
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Detect faces and get their encodings
face_locations = face_recognition.face_locations(rgb_frame)
face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

print(f"Detected {len(face_encodings)} face(s).")

# Match detected faces with known encodings
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    match_found = False
    matched_name = "Unknown"

    for student_id, student_encodings in known_encodings.items():
        for encoding in student_encodings:
            match = face_recognition.compare_faces([encoding], face_encoding)
            if match[0]:
                matched_name = student_id
                match_found = True
                break
        if match_found:
            break

    # Draw bounding box and name
    color = (0, 255, 0) if match_found else (0, 0, 255)  # Green for match, red for unknown
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    cv2.putText(frame, matched_name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

cv2.imshow('Matched Faces', frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

print("Test completed.")
