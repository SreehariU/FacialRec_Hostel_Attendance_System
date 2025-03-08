import cv2
import os
import sys

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATASET_PATH = os.path.join(BASE_PATH, "dataset")

def process_images(student_id):
    """
    Process images for a given student, detecting faces and saving processed images.
    """
    student_folder = os.path.join(DATASET_PATH, student_id)
    
    if not os.path.exists(student_folder):
        print(f"❌ Error: Student folder not found: {student_folder}")
        return False

    output_folder = os.path.join(student_folder, "processed")
    os.makedirs(output_folder, exist_ok=True)

    # Load face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    processed_count = 0

    for img_name in os.listdir(student_folder):
        img_path = os.path.join(student_folder, img_name)

        # Skip non-image files
        if not img_name.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        img = cv2.imread(img_path)
        if img is None:
            print(f"⚠️ Warning: Failed to read image: {img_path}")
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) == 0:
            print(f"⚠️ Warning: No faces detected in {img_name}")
            continue

        # Process each detected face
        for idx, (x, y, w, h) in enumerate(faces):
            face = img[y:y+h, x:x+w]
            resized_face = cv2.resize(face, (160, 160))
            
            output_file = os.path.join(output_folder, f"{img_name.split('.')[0]}_face{processed_count + 1}.jpg")
            cv2.imwrite(output_file, resized_face)
            print(f"✅ Saved processed face: {output_file}")
            processed_count += 1

    if processed_count > 0:
        print(f"✅ Successfully processed {processed_count} face images for {student_id}.")
        return True
    else:
        print("⚠️ No faces processed.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python Datacollection.py <student_id>")
        sys.exit(1)

    student_id = sys.argv[1]
    success = process_images(student_id)
    sys.exit(0 if success else 1)
