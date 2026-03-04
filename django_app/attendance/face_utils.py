"""
Face recognition core utilities.
Wraps the KNN-based face recognition logic from test.py and add_faces.py.
"""

import cv2
import pickle
import numpy as np
import os
import csv
import time
import threading
from datetime import datetime
from django.conf import settings

FACE_DATA_DIR = settings.FACE_DATA_DIR
ATTENDANCE_DIR = settings.ATTENDANCE_DIR
FACE_DIM = (50, 50)
HAARCASCADE = str(FACE_DATA_DIR / "haarcascade_frontalface_default.xml")


# ---------------------------------------------------------------------------
# KNN classifier – loaded once, reloaded when data changes
# ---------------------------------------------------------------------------


def load_knn():
    """
    Load KNN classifier from saved face data.
    Returns (knn, labels, threshold) or (None, None, None) if data missing.

    The `threshold` is a distance value computed from the training data:
    any prediction whose mean neighbour distance exceeds it is labelled
    "Unknown", preventing the model from forcing every face into a known class.
    """
    names_path = FACE_DATA_DIR / "names.pkl"
    faces_path = FACE_DATA_DIR / "faces_data.pkl"
    if not names_path.exists() or not faces_path.exists():
        return None, None, None
    try:
        from sklearn.neighbors import KNeighborsClassifier

        with open(names_path, "rb") as f:
            labels = pickle.load(f)
        with open(faces_path, "rb") as f:
            faces = pickle.load(f)

        n_neighbors = min(5, len(faces))
        knn = KNeighborsClassifier(n_neighbors=n_neighbors)
        knn.fit(faces, labels)

        # --- Compute dynamic unknown-rejection threshold ---
        # Query each training sample against the training set.
        # The first returned neighbour is the sample itself (distance ≈ 0),
        # so we skip it and look at the remaining ones.
        dists, _ = knn.kneighbors(faces)  # shape (n_samples, n_neighbors)
        if dists.shape[1] > 1:
            intra = dists[:, 1:]  # skip self-match
        else:
            intra = dists
        mean_d = float(np.mean(intra))
        std_d = float(np.std(intra))
        # Allow up to 2.5 standard deviations above the mean intra-class
        # distance; faces further away than this are treated as Unknown.
        threshold = mean_d + 2.5 * std_d

        return knn, labels, threshold
    except Exception:
        return None, None, None


# ---------------------------------------------------------------------------
# Attendance recording helper
# ---------------------------------------------------------------------------


def record_attendance(name: str):
    """Write a single attendance entry to today's CSV file."""
    os.makedirs(ATTENDANCE_DIR, exist_ok=True)
    date = datetime.now().strftime("%d-%m-%Y")
    timestamp = datetime.now().strftime("%H:%M:%S")
    file_path = ATTENDANCE_DIR / f"Attendance_{date}.csv"
    write_header = not file_path.exists()
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["NAME", "TIME"])
        writer.writerow([name, timestamp])
    return date, timestamp


# ---------------------------------------------------------------------------
# FaceCamera – MJPEG streaming with live recognition
# ---------------------------------------------------------------------------


class FaceCamera:
    """
    Thread-safe webcam wrapper that yields JPEG frames for MJPEG streaming.
    Automatically performs face recognition and marks attendance when a face
    is detected consistently (press 'o' key equivalent via mark_attendance()).
    """

    def __init__(self):
        self._cap = None
        self._lock = threading.Lock()
        self._running = False
        self._knn = None
        self._threshold = None  # distance threshold for Unknown rejection
        self._current_name = None
        self._frame = None
        self._frame_id = 0
        self._thread = None

    # ------------------------------------------------------------------
    def start(self):
        if self._running:
            return
        # Use DirectShow backend on Windows for faster, reliable open
        self._cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self._cap.isOpened():
            # Fallback to default backend
            self._cap = cv2.VideoCapture(0)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self._cap.set(cv2.CAP_PROP_FPS, 30)
        self._knn, _, self._threshold = load_knn()
        self._running = True
        self._frame_id = 0  # incremented each time a new frame is stored
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        time.sleep(0.15)  # let the capture thread exit cleanly
        if self._cap:
            self._cap.release()
            self._cap = None
        self._frame = None
        self._frame_id = 0

    def mark_attendance(self):
        """Call this to record attendance for the currently detected person."""
        name = self._current_name
        if name:
            date, ts = record_attendance(name)
            return name, date, ts
        return None, None, None

    def get_current_name(self):
        return self._current_name

    # ------------------------------------------------------------------
    def _capture_loop(self):
        facedetect = cv2.CascadeClassifier(HAARCASCADE)
        fail_count = 0
        while self._running:
            if self._cap is None or not self._cap.isOpened():
                break
            ret, frame = self._cap.read()
            if not ret:
                fail_count += 1
                if fail_count > 30:
                    # Camera died – try to reopen once
                    self._cap.release()
                    self._cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    fail_count = 0
                time.sleep(0.03)
                continue
            fail_count = 0

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = facedetect.detectMultiScale(gray, 1.3, 5)
            detected_name = None

            for x, y, w, h in faces:
                crop = frame[y : y + h, x : x + w, :]
                resized = cv2.resize(crop, FACE_DIM).flatten().reshape(1, -1)

                label = "Unknown"
                if self._knn is not None:
                    try:
                        # Get distances to k nearest neighbours.
                        # Use mean distance to decide if the face is known.
                        dists, _ = self._knn.kneighbors(resized)  # (1, k)
                        mean_dist = float(np.mean(dists[0]))
                        if self._threshold is None or mean_dist <= self._threshold:
                            label = self._knn.predict(resized)[0]
                        # else: label stays "Unknown"
                    except Exception:
                        pass
                detected_name = label if label != "Unknown" else None

                # Draw bounding box – red for known, orange for Unknown
                box_color = (50, 50, 255) if label != "Unknown" else (0, 140, 255)
                cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                cv2.rectangle(frame, (x, y - 40), (x + w, y), box_color, -1)
                cv2.putText(
                    frame,
                    str(label),
                    (x + 5, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2,
                )

            # Overlay date/time
            now_str = datetime.now().strftime("%d-%m-%Y  %H:%M:%S")
            cv2.putText(
                frame,
                now_str,
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                1,
            )

            # Overlay instruction
            cv2.putText(
                frame,
                "Press [Mark Attendance] to record",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                1,
            )

            with self._lock:
                self._current_name = detected_name
                self._frame = frame.copy()
                self._frame_id += 1

    # ------------------------------------------------------------------
    def generate_frames(self):
        """Generator yielding MJPEG multipart data at ~30 fps."""
        last_id = -1
        while True:
            with self._lock:
                frame = self._frame
                fid = self._frame_id

            if frame is None or fid == last_id:
                # No new frame yet – wait a short time before polling again
                time.sleep(0.03)
                continue

            last_id = fid
            ret, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if not ret:
                time.sleep(0.03)
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )
            # Throttle to ~30 fps maximum
            time.sleep(0.033)


# Singleton camera instance
_camera: FaceCamera = None


def get_camera() -> FaceCamera:
    global _camera
    if _camera is None:
        _camera = FaceCamera()
    # Restart if previously stopped
    if not _camera._running:
        _camera.start()
    return _camera


# ---------------------------------------------------------------------------
# Face capture for registration (add student)
# ---------------------------------------------------------------------------


class FaceCapture:
    """
    Capture face samples for a new student during the admin registration flow.
    Runs in a background thread; exposes a generator for MJPEG preview.
    """

    MAX_SAMPLES = 100

    def __init__(self, student_name: str, student_id: str):
        self.student_name = student_name
        self.student_id = student_id
        self._cap = None
        self._lock = threading.Lock()
        self._frame = None
        self._faces_data = []
        self._running = False
        self._done = False
        self._thread = None

    def start(self):
        # Release the global FaceCamera so both don't fight over camera 0
        global _camera
        if _camera is not None and _camera._running:
            _camera.stop()
        time.sleep(0.4)  # give the OS time to fully release the device
        self._cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self._cap.isOpened():
            self._cap = cv2.VideoCapture(0)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._cap:
            self._cap.release()

    def is_done(self):
        return self._done

    def samples_collected(self):
        return len(self._faces_data)

    def _capture_loop(self):
        facedetect = cv2.CascadeClassifier(HAARCASCADE)
        i = 0
        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = facedetect.detectMultiScale(gray, 1.3, 5)
            for x, y, w, h in faces:
                crop = frame[y : y + h, x : x + w, :]
                resized = cv2.resize(crop, FACE_DIM)
                if len(self._faces_data) < self.MAX_SAMPLES and i % 10 == 0:
                    self._faces_data.append(resized)
                i += 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)
            count = len(self._faces_data)
            cv2.putText(
                frame,
                f"Samples: {count}/{self.MAX_SAMPLES}",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 200, 0),
                2,
            )
            with self._lock:
                self._frame = frame.copy()
            if len(self._faces_data) >= self.MAX_SAMPLES:
                self._save_and_finish()
                break

    def _save_and_finish(self):
        faces_data = np.asarray(self._faces_data).reshape(len(self._faces_data), -1)
        os.makedirs(FACE_DATA_DIR, exist_ok=True)
        names_path = FACE_DATA_DIR / "names.pkl"
        faces_path = FACE_DATA_DIR / "faces_data.pkl"

        # names
        label = self.student_name
        if names_path.exists():
            with open(names_path, "rb") as f:
                names = pickle.load(f)
            names += [label] * len(faces_data)
        else:
            names = [label] * len(faces_data)
        with open(names_path, "wb") as f:
            pickle.dump(names, f)

        # faces
        if faces_path.exists():
            with open(faces_path, "rb") as f:
                existing = pickle.load(f)
            faces_data = np.vstack([existing, faces_data])
        with open(faces_path, "wb") as f:
            pickle.dump(faces_data, f)

        self._running = False
        self._done = True
        if self._cap:
            self._cap.release()
            self._cap = None
        # Reset the global camera so get_camera() starts it fresh with
        # updated KNN data the next time the student page is opened.
        global _camera
        _camera = None

    def generate_frames(self):
        while not self._done:
            with self._lock:
                frame = self._frame
            if frame is None:
                time.sleep(0.05)
                continue
            ret, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not ret:
                time.sleep(0.05)
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
            )
            time.sleep(0.033)
