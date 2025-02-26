import cv2
import os  
import face_recognition
import numpy as np
import pickle

# Dataset path
dataset_path = "dataset"
encodings = []
labels = []
label_dict = {}

# Process each user's folder
for person_name in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person_name)

    if not os.path.isdir(person_path):
        continue

    # Use folder name (person_name) as label
    user_id = person_name
    label_dict[user_id] = person_name  # Map name to itself (no database ID)

    # Process images in the user's folder
    for image_name in os.listdir(person_path):
        image_path = os.path.join(person_path, image_name)

        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Couldn't read image {image_path}. Skipping...")
            continue

        # Convert to RGB for FaceNet
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_img)

        if len(face_encodings) > 0:
            encodings.append(face_encodings[0])
            labels.append(user_id)

# Save the face encodings and labels
data = {"encodings": encodings, "labels": labels, "label_dict": label_dict}
with open("face_encodings.pkl", "wb") as f:
    pickle.dump(data, f)

print("Training Complete! Model saved as face_encodings.pkl")
