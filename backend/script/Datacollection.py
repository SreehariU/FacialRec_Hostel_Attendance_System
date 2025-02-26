import cv2
import os

# Load OpenCV's face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Create dataset directory
dataset_path = "dataset"
os.makedirs(dataset_path, exist_ok=True)

# Get user input for name (to be used as label)
person_name = input("Enter your name (no spaces): ").strip()
if not person_name:
    print("Name cannot be empty. Exiting...")
    exit()

# Ensure folder for the person exists
person_folder = os.path.join(dataset_path, person_name)
os.makedirs(person_folder, exist_ok=True)

# Initialize webcam
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("Error: Could not access webcam")
    exit()

count = 0
max_images = 50

print(f"Collecting {max_images} images for {person_name}. Look into the camera...")

try:
    while count < max_images:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to capture image. Exiting...")
            break

        # Convert to grayscale for detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            count += 1

            # Crop and resize face to 160x160
            face = frame[y:y+h, x:x+w]
            face = cv2.resize(face, (160, 160))

            # Save image with incremented count
            img_path = os.path.join(person_folder, f"{person_name}_{count}.jpg")
            cv2.imwrite(img_path, face)

            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Show camera feed
        cv2.imshow("Face Collection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(f"Collected {count} images for {person_name}.")
finally:
    video_capture.release()
    cv2.destroyAllWindows()
