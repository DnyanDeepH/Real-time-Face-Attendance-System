from django.urls import path
from . import views

urlpatterns = [
    # Landing
    path("", views.landing, name="landing"),
    # Auth
    path("login/", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    # Student flow
    path("student/", views.student_camera, name="student_camera"),
    path("student/video/", views.student_video_feed, name="student_video_feed"),
    path(
        "student/mark/", views.student_mark_attendance, name="student_mark_attendance"
    ),
    path("student/stop/", views.student_stop_camera, name="student_stop_camera"),
    # Admin panel
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    # Student management
    path("admin-panel/students/", views.student_list, name="student_list"),
    path("admin-panel/students/add/", views.add_student, name="add_student"),
    path(
        "admin-panel/students/add/capture/<str:student_id>/",
        views.capture_face,
        name="capture_face",
    ),
    path(
        "admin-panel/students/add/capture/<str:student_id>/feed/",
        views.capture_feed,
        name="capture_feed",
    ),
    path(
        "admin-panel/students/add/capture/<str:student_id>/status/",
        views.capture_status,
        name="capture_status",
    ),
    path(
        "admin-panel/students/<int:pk>/delete/",
        views.delete_student,
        name="delete_student",
    ),
    # Attendance reports
    path(
        "admin-panel/attendance/",
        views.attendance_report_index,
        name="attendance_index",
    ),
    path(
        "admin-panel/attendance/<str:date_str>/",
        views.attendance_by_date,
        name="attendance_by_date",
    ),
    path(
        "admin-panel/attendance/<str:date_str>/download/",
        views.download_attendance_csv,
        name="download_attendance_csv",
    ),
    path(
        "admin-panel/report/",
        views.attendance_percentage_report,
        name="attendance_report",
    ),
]
