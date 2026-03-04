# 🎯 Real-time Face Attendance System

![Face Recognition](https://img.shields.io/badge/Face-Recognition-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
![Django](https://img.shields.io/badge/Django-4.2-green)
![KNN](https://img.shields.io/badge/ML-KNN%20Classifier-orange)

A real-time face recognition–based attendance system with a **Django web frontend**. The system uses a webcam to detect and identify registered students, logs attendance automatically, and provides a full administrator portal for managing students and viewing reports.

---

## 📖 Project Overview

| Role | Access |
|---|---|
| **Administrator** | Login required → full dashboard (add/remove students, view attendance, reports) |
| **Student** | No login → directly opens camera → presses Mark Attendance |

---

## ✨ Features

### 👤 Student
- Direct camera access — no login required
- Live face recognition with bounding box overlay
- One-click **Mark Attendance** button
- Unknown faces are rejected (will not mark attendance)

### 🛡️ Administrator
- Secure login portal
- **Register students** — fill details + live 100-sample face capture via webcam
- **Remove students** from the system
- View **total registered students**
- View **date-wise attendance records** (present / absent / on leave)
- **Download attendance CSV** for any date
- **Attendance percentage report** for all students
- Automatic flagging of students **below 75% attendance**

---

## 🧰 Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| Django 4.2 | Web framework (backend + frontend) |
| OpenCV | Webcam capture, face detection (Haar Cascade) |
| scikit-learn | KNN classifier for face recognition |
| NumPy | Matrix / array operations |
| Pandas | CSV attendance file handling |
| SQLite | Student & session database |
| HTML / CSS / JS | Dark-themed custom UI |

---

## 📁 Project Structure

```
Real time Face Attendance System/
│
├── django_app/                     ← Django project root
│   ├── manage.py                   ← Django management script
│   ├── requirements.txt            ← Python dependencies
│   ├── db.sqlite3                  ← Auto-created SQLite database
│   │
│   ├── face_attendance/            ← Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── attendance/                 ← Main Django app
│   │   ├── models.py               ← Student, AdminCredential models
│   │   ├── views.py                ← All page & API views
│   │   ├── urls.py                 ← URL routing
│   │   ├── forms.py                ← Login & student registration forms
│   │   ├── face_utils.py           ← Threaded face recognition engine
│   │   └── migrations/
│   │
│   ├── templates/                  ← HTML templates
│   │   ├── base.html               ← Sidebar layout (admin)
│   │   ├── landing.html            ← Role selector page
│   │   ├── login.html              ← Admin login
│   │   ├── student/
│   │   │   └── camera.html         ← Student attendance camera
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── students.html
│   │       ├── add_student.html
│   │       ├── capture_face.html
│   │       ├── attendance_index.html
│   │       ├── attendance_by_date.html
│   │       └── report.html
│   │
│   └── static/
│       ├── css/style.css           ← Dark theme styles
│       └── js/main.js
│
├── data/                           ← Face model data (stored here)
│   ├── haarcascade_frontalface_default.xml
│   ├── names.pkl                   ← Student name labels (created on first registration)
│   └── faces_data.pkl              ← Face vectors (created on first registration)
│
├── Attendance/                     ← CSV attendance files (auto-created daily)
│   └── Attendance_DD-MM-YYYY.csv
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.6 or higher
- Webcam or camera device
- Git and terminal access
- Required Python libraries

### 🔧 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/<your-username>/face-attendance-system.git
   cd face-attendance-system
   ```

2. **Install the required dependencies**  
   ```bash
   pip install opencv-python scikit-learn pandas numpy streamlit streamlit-autorefresh pywin32
   ```

---

### Step 2 — Install dependencies

```powershell
cd django_app
pip install -r requirements.txt
```

`requirements.txt` contents:
```
Django>=4.2,<5.0
opencv-python>=4.8
scikit-learn>=1.3
numpy>=1.24
pandas>=2.0
```

---

### Step 3 — Apply database migrations

```powershell
python manage.py migrate
```

This creates `db.sqlite3` with the `Student` and session tables.

---

### Step 4 — Run the development server

```powershell
python manage.py runserver 8000
```

Open your browser at: **http://127.0.0.1:8000/**

---

## 🖥️ Using the Application

### Landing Page — `http://127.0.0.1:8000/`

Choose your role:

| Button | Goes to |
|---|---|
| **Administrator** | Admin login page |
| **Student** | Live camera for attendance |

---

### 🛡️ Admin Login — `/login/`

| Field | Default Value |
|---|---|
| Username | `admin` |
| Password | `admin123` |

> **Change the password** after first use by editing `ADMIN_PASSWORD` in `django_app/attendance/views.py`.

---

### 🛡️ Admin Dashboard — `/admin-panel/`

After logging in, the sidebar gives access to all admin features.

#### 👥 Students — `/admin-panel/students/`
- View all registered students with name, ID, department, and date registered
- Click **Remove** to deactivate a student

#### ➕ Register New Student — `/admin-panel/students/add/`
1. Fill in: **Student ID / Roll No**, **Name**, **Email** (optional), **Department**
2. Click **Next: Capture Face →**
3. The webcam opens automatically — the student should look directly at the camera
4. 100 face samples are captured automatically (progress bar shown)
5. Once complete, the face data is saved and the recognition model updates instantly

#### 📅 Attendance Records — `/admin-panel/attendance/`
- Lists all dates where attendance was recorded (newest first)
- Click any date to see:
  - ✅ **Present** students (name + time marked)
  - ❌ **Absent / On Leave** students (registered students not present that day)
- Download the day's attendance as a **CSV file**

#### 📊 Attendance Report — `/admin-panel/report/`
- Attendance **percentage** for every registered student across all recorded dates
- Progress bar coloured by status:
  - 🟢 **Green** — ≥ 75% (Good Standing)
  - 🟡 **Yellow** — 60–74% (Warning)
  - 🔴 **Red** — < 60% (Below Threshold)
- Students below **75%** are also flagged on the dashboard home

---

### 📷 Student Camera — `/student/`

1. Open the page — the webcam starts automatically
2. Look at the camera — your name appears in the bounding box if you are registered
3. Press **✅ Mark Attendance** when your name appears
4. A confirmation is shown: name, date, and time
5. If your face is **not recognised** (Unknown), attendance is blocked with an error message

---

## ⚙️ How Face Recognition Works

```
Webcam frame
    ↓
Haar Cascade face detection  →  face region cropped
    ↓
Resize to 50×50 px and flatten to 1-D vector
    ↓
KNN Classifier (k = 5)
    ↓
Distance check:
  mean_distance ≤ threshold  →  Known person (label shown, green box)
  mean_distance >  threshold  →  Unknown  (orange box, no attendance)
    ↓
If Known → write NAME + TIME to Attendance/Attendance_DD-MM-YYYY.csv
```

The **Unknown rejection threshold** is computed automatically from training data:  
`threshold = mean_intra_class_distance + 2.5 × std_deviation`

---

## 🔐 Default Admin Credentials

```
Username : admin
Password : admin123
```

**To change credentials**, edit `django_app/attendance/views.py`:
```python
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'   # ← change this line
```

---

## 🛠️ Common Issues & Fixes

| Problem | Fix |
|---|---|
| Camera not opening / frozen | Ensure no other app is using the webcam. Restart the server. |
| "No face detected" when marking | Improve lighting, face camera directly, move closer. |
| Unknown shown for registered student | Re-register with better lighting. Threshold auto-adjusts with more samples. |
| Template syntax error after saving | Disable auto-formatter (Prettier) for `templates/`. Add `templates/` to `.prettierignore`. |
| Port 8000 already in use | Run: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F` |
| `migrate` fails | Delete `db.sqlite3` and re-run `python manage.py migrate` |

---

## 📜 URL Reference

| URL | Description |
|---|---|
| `/` | Landing — role selector |
| `/login/` | Admin login |
| `/logout/` | Admin logout |
| `/student/` | Student camera page |
| `/student/video/` | MJPEG live camera stream |
| `/student/mark/` | POST — mark attendance (AJAX) |
| `/admin-panel/` | Admin dashboard |
| `/admin-panel/students/` | Student list |
| `/admin-panel/students/add/` | Add new student |
| `/admin-panel/attendance/` | All attendance dates |
| `/admin-panel/attendance/<DD-MM-YYYY>/` | Attendance for a specific date |
| `/admin-panel/attendance/<DD-MM-YYYY>/download/` | Download CSV |
| `/admin-panel/report/` | Attendance percentage report |

---

## 👨‍💻 Project Info

**Roll No:** 12410248  
**Subject:** CAP450 – Intelligent & Interactive Systems  
**Activity:** 05 – Real-time Face Attendance System  
**Framework:** Django 4.2 + OpenCV + KNN Classifier

---

## 📜 License

This project is developed for academic purposes under MCA Semester 2.
