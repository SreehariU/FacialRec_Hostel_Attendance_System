import cv2
import face_recognition
import numpy as np
import pickle
import time

# Load trained FaceNet encodings
try:
    with open("face_encodings.pkl", "rb") as f:
        data = pickle.load(f)
    
    encodings = np.array(data["encodings"])
    labels = np.array(data["labels"])  # Keep names as strings, not integers
    label_dict = data.get("label_dict", {})  # Ensure label_dict exists
except FileNotFoundError:
    print("Error: face_encodings.pkl not found!")
    exit()

# Initialize video capture
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("Error: Could not access webcam")
    exit()

# Performance metrics
frame_count = 0
start_time = time.perf_counter()
fps = 0.0

try:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        # Convert frame to RGB for face recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
        
        # Detect faces
        face_locations = face_recognition.face_locations(small_frame)
        face_locations = [(t*4, r*4, b*4, l*4) for (t, r, b, l) in face_locations]
        
        # Recognize faces
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            face_distances = face_recognition.face_distance(encodings, face_encoding)
            match_index = np.argmin(face_distances)
            confidence = 1 - face_distances[match_index]
            
            name = "Unknown"
            if face_distances[match_index] < 0.5:
                name = f"{labels[match_index]} ({confidence:.2f})"

            # Draw bounding box and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 15), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Calculate FPS
        frame_count += 1
        if frame_count >= 30:
            fps = frame_count / (time.perf_counter() - start_time)
            start_time = time.perf_counter()
            frame_count = 0

        # Display FPS
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show output frame
        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # Cleanup
    video_capture.release()
    cv2.destroyAllWindows()
    print("Resources cleaned up successfully.")
