# 🎯 Real-time Face Attendance System

![Face Recognition](https://img.shields.io/badge/Face-Recognition-brightgreen)
![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-orange)

A real-time face recognition-based attendance system built using Python, OpenCV, and Streamlit. This project enables institutions and organizations to automate attendance tracking using facial recognition, reducing manual efforts and increasing reliability.

---

## 📖 Project Overview

This system captures real-time video from a webcam, detects and recognizes faces, and logs attendance with timestamps. Users can interact with a Streamlit-based web interface that visualizes attendance data, provides search functionality, and allows data export in CSV format. It is ideal for classrooms, workplaces, or any group setting requiring automated attendance tracking.

---

## 🧰 Features

✅ **Face Detection & Recognition** – Powered by OpenCV and KNN classifier  
✅ **Real-time Processing** – Live video stream face identification  
✅ **Attendance Logging** – Automatic recording with name and time  
✅ **Streamlit Dashboard** – Visual display of attendance, stats, and CSV download  
✅ **Search Option** – Search for a person’s records easily  
✅ **CSV Export** – Download attendance logs anytime  
✅ **Data Visualization** – Track attendance trends with charts and tables

---

## 💻 Technologies Used

| Technology       | Purpose                                  |
|------------------|------------------------------------------|
| Python           | Core development language                |
| OpenCV           | Face detection and video feed handling   |
| scikit-learn     | KNN classifier for face recognition      |
| Haar Cascade     | Pre-trained face detection model         |
| Streamlit        | Interactive frontend interface           |
| Pandas           | CSV data handling                        |
| NumPy            | Matrix and array operations              |

---

## 🚀 Getting Started

### 📌 Prerequisites

- Python 3.6 or higher
- Webcam or camera device
- Git and terminal access
- Required Python libraries

### 🔧 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/DnyanDeepH/Real-time-Face-Attendance-System.git
   cd Real-time-Face-Attendance-System
   ```

2. **Install the required dependencies**  
   ```bash
   pip install opencv-python scikit-learn pandas numpy streamlit streamlit-autorefresh pywin32
   ```

---

## ▶️ How to Use

1. **Add New Faces**  
   Run the following script to capture and save face data:
   ```bash
   python add_faces.py
   ```

2. **Train and Test the Model**  
   Use this script to check recognition:
   ```bash
   python test.py
   ```

3. **Run the Streamlit Dashboard**  
   Launch the attendance web interface:
   ```bash
   streamlit run app.py
   ```

---

## 📁 Project Structure

```
face-attendance-system/
├── add_faces.py         # Script to register new users
├── test.py              # Face recognition script
├── app.py               # Streamlit dashboard
├── data/                # Stores face images and CSV logs
├── model/               # Trained face encoding data
└── README.md            # Project documentation
```

---

## 👌 Contribution

We welcome contributions to improve the system! Fork the repository, make your changes, and submit a pull request. Let’s build smarter attendance solutions together.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

