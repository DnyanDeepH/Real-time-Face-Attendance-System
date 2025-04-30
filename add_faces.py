import cv2
import pickle
import numpy as np
import os

# Create Attendance directory if it doesn't exist
if not os.path.exists('Attendance'):
    os.makedirs('Attendance')

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

faces_data = []

i = 0
max_samples = 100  # Number of face samples to collect

name = input("Enter Your Name: ")

# Check if faces_data.pkl exists to determine the correct dimensions
face_dimensions = (50, 50)  # Default dimensions
if os.path.exists('data/faces_data.pkl'):
    try:
        with open('data/faces_data.pkl', 'rb') as f:
            existing_faces = pickle.load(f)
            # Calculate dimensions from existing data
            if existing_faces.shape[1] == 3075:  # 41×25×3 flattened
                face_dimensions = (41, 25)
                print(f"Using existing dimensions: {face_dimensions}")
            else:
                print(f"Using dimensions: {face_dimensions}")
    except Exception as e:
        print(f"Error reading existing data: {e}")
        print(f"Using default dimensions: {face_dimensions}")
else:
    print(f"No existing data found. Using dimensions: {face_dimensions}")

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to grab frame")
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        crop_img = frame[y:y+h, x:x+w, :]
        # Use the dimensions determined above
        resized_img = cv2.resize(crop_img, face_dimensions)
        
        if len(faces_data) < max_samples and i % 10 == 0:
            faces_data.append(resized_img)
            
        i = i + 1
        cv2.putText(frame, f"{len(faces_data)}/{max_samples}", (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)
    
    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    
    if k == ord('q') or len(faces_data) >= max_samples:
        break

video.release()
cv2.destroyAllWindows()

# Check if we collected any faces
if len(faces_data) == 0:
    print("No faces detected. Please try again.")
    exit()

# Convert to numpy array
faces_data = np.asarray(faces_data)
# Reshape for the classifier (flattening the images)
faces_data = faces_data.reshape(len(faces_data), -1)

# Ensure data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Handle names.pkl file
if 'names.pkl' not in os.listdir('data/'):
    names = [name] * len(faces_data)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)
else:
    with open('data/names.pkl', 'rb') as f:
        names = pickle.load(f)
    names = names + [name] * len(faces_data)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)

# Handle faces_data.pkl file
if 'faces_data.pkl' not in os.listdir('data/'):
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces_data, f)
else:
    with open('data/faces_data.pkl', 'rb') as f:
        faces = pickle.load(f)
    # Verify dimensions match before appending
    if faces.shape[1] != faces_data.shape[1]:
        print(f"Error: Dimension mismatch. Existing data has {faces.shape[1]} features per face, ")
        print(f"but new data has {faces_data.shape[1]} features per face.")
        print("Please delete the existing data files and start fresh, or modify the code to use consistent dimensions.")
        exit(1)
    faces = np.append(faces, faces_data, axis=0)
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces, f)

print(f"Training data for {name} has been saved successfully!")