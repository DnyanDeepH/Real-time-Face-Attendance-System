"""
All views for the Face Attendance System (Django).

URL layout:
    /                   → Landing / role selector
    /login/             → Admin login
    /logout/            → Admin logout
    /student/           → Student camera (mark attendance)
    /student/video/     → MJPEG stream (student)
    /student/mark/      → AJAX – mark attendance
    /admin-panel/       → Admin dashboard
    /admin-panel/students/         → Registered students list
    /admin-panel/students/add/     → Add student + capture face
    /admin-panel/students/add/capture-feed/  → MJPEG stream during capture
    /admin-panel/students/add/status/        → AJAX poll capture status
    /admin-panel/students/<id>/delete/       → Delete student
    /admin-panel/attendance/       → Date-wise attendance report
    /admin-panel/attendance/<date>/  → Attendance for a specific date
    /admin-panel/report/             → Attendance % / low-attendance report
"""

import os
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

import pandas as pd
from django.conf import settings
from django.http import StreamingHttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Student, AdminCredential
from .forms import AdminLoginForm, AddStudentForm
from .face_utils import get_camera, FaceCapture

ATTENDANCE_DIR = settings.ATTENDANCE_DIR
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Change after first run

# Active face capture sessions keyed by student_id
_capture_sessions: dict[str, FaceCapture] = {}


# ============================================================
#  Helper: require admin session
# ============================================================


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("is_admin"):
            return redirect("login")
        return view_func(request, *args, **kwargs)

    wrapper.__name__ = view_func.__name__
    return wrapper


# ============================================================
#  Landing page
# ============================================================


def landing(request):
    return render(request, "landing.html")


# ============================================================
#  Admin Login / Logout
# ============================================================


def admin_login(request):
    if request.session.get("is_admin"):
        return redirect("admin_dashboard")

    error = None
    if request.method == "POST":
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data["username"]
            pwd = form.cleaned_data["password"]
            # Check DB first; fall back to hard-coded defaults
            try:
                cred = AdminCredential.objects.get(username=uname)
                valid = cred.password == pwd
            except AdminCredential.DoesNotExist:
                valid = uname == ADMIN_USERNAME and pwd == ADMIN_PASSWORD
            if valid:
                request.session["is_admin"] = True
                request.session["admin_username"] = uname
                return redirect("admin_dashboard")
            else:
                error = "Invalid username or password."
    else:
        form = AdminLoginForm()

    return render(request, "login.html", {"form": form, "error": error})


def admin_logout(request):
    request.session.flush()
    return redirect("landing")


# ============================================================
#  Student Camera View
# ============================================================


def student_camera(request):
    """Page where a student marks their attendance via camera."""
    get_camera()  # ensures camera is started
    return render(request, "student/camera.html")


def student_video_feed(request):
    cam = get_camera()
    return StreamingHttpResponse(
        cam.generate_frames(), content_type="multipart/x-mixed-replace; boundary=frame"
    )


@csrf_exempt
def student_mark_attendance(request):
    """AJAX endpoint: mark attendance for the person currently in camera."""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST required"})
    cam = get_camera()
    name, date, ts = cam.mark_attendance()
    if name:
        return JsonResponse(
            {
                "success": True,
                "name": name,
                "date": date,
                "time": ts,
                "message": f"Attendance recorded for {name} at {ts}",
            }
        )
    return JsonResponse(
        {"success": False, "message": "No face detected. Please look at the camera."}
    )


def student_stop_camera(request):
    cam = get_camera()
    cam.stop()
    return redirect("landing")


# ============================================================
#  Admin Dashboard
# ============================================================


@admin_required
def admin_dashboard(request):
    total_students = Student.objects.filter(is_active=True).count()

    # Today's attendance
    today_str = datetime.now().strftime("%d-%m-%Y")
    today_file = ATTENDANCE_DIR / f"Attendance_{today_str}.csv"
    today_count = 0
    today_names = set()
    if today_file.exists():
        df = pd.read_csv(today_file)
        today_count = df["NAME"].nunique() if "NAME" in df.columns else 0
        today_names = set(df["NAME"].tolist()) if "NAME" in df.columns else set()

    absent_today = total_students - today_count

    # Available attendance dates
    dates = _get_available_dates()

    # Low attendance students
    low_att = _compute_low_attendance(threshold=75)

    context = {
        "total_students": total_students,
        "today_present": today_count,
        "today_absent": absent_today,
        "today_date": today_str,
        "dates": dates[:5],  # recent 5
        "low_att_students": low_att,
        "admin_username": request.session.get("admin_username", "Admin"),
    }
    return render(request, "admin/dashboard.html", context)


# ============================================================
#  Student Management
# ============================================================


@admin_required
def student_list(request):
    students = Student.objects.filter(is_active=True).order_by("name")
    return render(
        request,
        "admin/students.html",
        {
            "students": students,
            "total": students.count(),
            "admin_username": request.session.get("admin_username", "Admin"),
        },
    )


@admin_required
def add_student(request):
    msg = None
    form = AddStudentForm()
    if request.method == "POST":
        form = AddStudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            # Start face capture session
            cap = FaceCapture(student.name, student.student_id)
            cap.start()
            _capture_sessions[student.student_id] = cap
            return redirect("capture_face", student_id=student.student_id)
    return render(
        request,
        "admin/add_student.html",
        {
            "form": form,
            "admin_username": request.session.get("admin_username", "Admin"),
        },
    )


@admin_required
def capture_face(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    return render(
        request,
        "admin/capture_face.html",
        {
            "student": student,
            "admin_username": request.session.get("admin_username", "Admin"),
        },
    )


def capture_feed(request, student_id):
    """MJPEG feed for face capture."""
    cap = _capture_sessions.get(student_id)
    if not cap:
        return HttpResponseForbidden("No active capture session.")
    return StreamingHttpResponse(
        cap.generate_frames(), content_type="multipart/x-mixed-replace; boundary=frame"
    )


def capture_status(request, student_id):
    """Poll endpoint: returns JSON with sample count and done flag."""
    cap = _capture_sessions.get(student_id)
    if not cap:
        return JsonResponse({"done": True, "samples": 0})
    done = cap.is_done()
    samples = cap.samples_collected()
    if done:
        _capture_sessions.pop(student_id, None)
        # _save_and_finish() already reset _camera = None, so the next time
        # the student page is opened, get_camera() will start fresh with the
        # newly trained KNN. Nothing more to do here.
    return JsonResponse(
        {"done": done, "samples": samples, "max": FaceCapture.MAX_SAMPLES}
    )


@admin_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    student.is_active = False
    student.save()
    return redirect("student_list")


# ============================================================
#  Attendance Reports
# ============================================================


@admin_required
def attendance_report_index(request):
    dates = _get_available_dates()
    return render(
        request,
        "admin/attendance_index.html",
        {
            "dates": dates,
            "admin_username": request.session.get("admin_username", "Admin"),
        },
    )


@admin_required
def attendance_by_date(request, date_str):
    file_path = ATTENDANCE_DIR / f"Attendance_{date_str}.csv"
    present = []
    absent_students = []
    if file_path.exists():
        df = pd.read_csv(file_path)
        if "NAME" in df.columns:
            present_names = set(df["NAME"].tolist())
            present = df.drop_duplicates(subset="NAME").to_dict("records")
        else:
            present_names = set()
        # Absent: registered students not in present list
        all_students = list(
            Student.objects.filter(is_active=True).values_list("name", flat=True)
        )
        absent_students = [s for s in all_students if s not in present_names]
    else:
        all_students = list(
            Student.objects.filter(is_active=True).values_list("name", flat=True)
        )
        absent_students = all_students

    return render(
        request,
        "admin/attendance_by_date.html",
        {
            "date_str": date_str,
            "present": present,
            "absent": absent_students,
            "total_present": len(present),
            "total_absent": len(absent_students),
            "admin_username": request.session.get("admin_username", "Admin"),
        },
    )


@admin_required
def attendance_percentage_report(request):
    """Show attendance % for all students and flag those below 75%."""
    stats = _compute_all_attendance_stats()
    low_att = [s for s in stats if s["percentage"] < 75]
    return render(
        request,
        "admin/report.html",
        {
            "stats": stats,
            "low_att": low_att,
            "admin_username": request.session.get("admin_username", "Admin"),
        },
    )


@admin_required
def download_attendance_csv(request, date_str):
    """Direct CSV download for a date."""
    file_path = ATTENDANCE_DIR / f"Attendance_{date_str}.csv"
    if not file_path.exists():
        return JsonResponse({"error": "File not found"}, status=404)
    with open(file_path, "r") as f:
        content = f.read()
    from django.http import HttpResponse

    response = HttpResponse(content, content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="Attendance_{date_str}.csv"'
    )
    return response


# ============================================================
#  Internal helpers
# ============================================================


def _get_available_dates():
    """Return sorted list of date strings extracted from Attendance CSV filenames (newest first)."""
    if not ATTENDANCE_DIR.exists():
        return []
    dates = []
    for f in ATTENDANCE_DIR.iterdir():
        if f.name.startswith("Attendance_") and f.name.endswith(".csv"):
            d = f.stem.replace("Attendance_", "")
            dates.append(d)
    # Sort descending (newest first) using parsed dates
    try:
        dates.sort(key=lambda d: datetime.strptime(d, "%d-%m-%Y"), reverse=True)
    except Exception:
        dates.sort(reverse=True)
    return dates


def _compute_low_attendance(threshold=75):
    """Return list of dicts for students below `threshold` attendance %."""
    return [s for s in _compute_all_attendance_stats() if s["percentage"] < threshold]


def _compute_all_attendance_stats():
    """
    Compute per-student attendance percentage across all recorded dates.
    Returns list of dicts: {name, present, total, percentage}
    """
    dates = _get_available_dates()
    total_days = len(dates)
    if total_days == 0:
        return []

    all_students = list(
        Student.objects.filter(is_active=True).values("name", "student_id")
    )
    presence: dict[str, int] = defaultdict(int)

    for date_str in dates:
        fp = ATTENDANCE_DIR / f"Attendance_{date_str}.csv"
        if not fp.exists():
            continue
        try:
            df = pd.read_csv(fp)
            if "NAME" not in df.columns:
                continue
            for name in df["NAME"].unique():
                presence[name] += 1
        except Exception:
            continue

    stats = []
    for st in all_students:
        name = st["name"]
        present = presence.get(name, 0)
        pct = round((present / total_days) * 100, 1) if total_days > 0 else 0
        stats.append(
            {
                "name": name,
                "student_id": st["student_id"],
                "present": present,
                "total": total_days,
                "percentage": pct,
            }
        )
    stats.sort(key=lambda x: x["percentage"])
    return stats
