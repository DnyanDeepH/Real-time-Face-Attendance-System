from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from win32com.client import Dispatch

def speak(str1):
    speak = Dispatch("SAPI.SpVoice")
    speak.Speak(str1)

# Ensure Attendance directory exists
if not os.path.exists('Attendance'):
    os.makedirs('Attendance')

# Check if model files exist
if not os.path.exists("data/names.pkl") or not os.path.exists("data/faces_data.pkl"):
    print("Error: Training data not found. Please run add_faces.py first.")
    exit()

video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier("data/haarcascade_frontalface_default.xml")

with open("data/names.pkl", "rb") as w:
    LABELS = pickle.load(w)
with open("data/faces_data.pkl", "rb") as f:
    FACES = pickle.load(f)

print("Shape of Faces matrix --> ", FACES.shape)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Load background image if it exists
try:
    imgBackground = cv2.imread("background.png")
    use_background = True
except:
    use_background = False
    print("Background image not found, using regular window.")

COL_NAMES = ["NAME", "TIME"]

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to grab frame")
        break
        
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)
    
    # Initialize attendance outside the loop
    attendance = None
    
    for x, y, w, h in faces:
        crop_img = frame[y:y+h, x:x+w, :]  # Use color image
        # Use the same dimensions as in add_faces.py
        resized_img = cv2.resize(crop_img, (50, 50))  
        resized_img = resized_img.flatten().reshape(1, -1)  # Flatten for prediction
        
        output = knn.predict(resized_img)
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M-%S")
        exist = os.path.isfile("Attendance/Attendance_" + date + ".csv")
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 2)
        cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
        cv2.putText(
            frame,
            str(output[0]),
            (x, y-15),
            cv2.FONT_HERSHEY_COMPLEX,
            1,
            (255, 255, 255),
            1,
        )
        attendance = [str(output[0]), str(timestamp)]
    
    # Display the frame
    if use_background and imgBackground is not None:
        try:
            imgBackground[162:162+480, 55:55+640] = frame
            cv2.imshow("Face Attendance", imgBackground)
        except:
            cv2.imshow("Face Attendance", frame)
    else:
        cv2.imshow("Face Attendance", frame)
    
    k = cv2.waitKey(1)
    if k == ord("o") and attendance is not None:
        speak("Attendance Taken..")
        time.sleep(1)  # Reduced from 5 seconds to 1 second for better UX
        if exist:
            with open("Attendance/Attendance_" + date + ".csv", "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(attendance)
        else:
            with open("Attendance/Attendance_" + date + ".csv", "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(COL_NAMES)
                writer.writerow(attendance)
        print(f"Attendance recorded for {attendance[0]}")
    if k == ord("q"):
        break

video.release()
cv2.destroyAllWindows()