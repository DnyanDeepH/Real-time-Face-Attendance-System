# Real-time Face Attendance System

![Face Recognition](https://img.shields.io/badge/Face-Recognition-brightgreen)
![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-orange)

A modern face recognition-based attendance system that automatically identifies individuals and maintains attendance records with a user-friendly dashboard.

## 📋 Features

- **Face Detection & Recognition**: Automatically detects and recognizes faces using OpenCV and machine learning
- **Real-time Processing**: Processes video feed in real-time for immediate recognition
- **Attendance Tracking**: Records attendance with timestamps in CSV format
- **User-friendly Dashboard**: Interactive Streamlit dashboard to view and analyze attendance data
- **Search Functionality**: Easily search for specific individuals in the attendance records
- **Data Visualization**: View attendance statistics and trends
- **Export Options**: Download attendance data in CSV format

## 🛠️ Technologies Used

- **Python**: Core programming language
- **OpenCV**: For face detection and image processing
- **scikit-learn**: For machine learning (KNN classifier)
- **Streamlit**: For the interactive web dashboard
- **Pandas**: For data manipulation and analysis
- **NumPy**: For numerical operations
- **Haar Cascade Classifier**: For face detection

## 🚀 Getting Started

### Prerequisites

- Python 3.6 or higher
- Webcam or camera device
- Required Python packages (see Installation)

### Installation

1. Clone this repository or download the source code

2. Install the required packages:

```bash
pip install opencv-python scikit-learn pandas numpy streamlit streamlit-autorefresh win32com

### Usage
1. Add faces to the dataset using the `add_faces.py` script.
    python add_faces.py

2. Run the `test.py` script to test the face recognition system.
    python test.py

3. Run the `app.py` script to start the Streamlit dashboard.
    streamlit run app.py



