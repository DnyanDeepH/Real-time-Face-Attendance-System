from django.db import models


class Student(models.Model):
    """Registered student in the face recognition system."""

    student_id = models.CharField(
        max_length=20, unique=True, verbose_name="Student ID / Roll No"
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, default="")
    date_registered = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class AdminCredential(models.Model):
    """Simple admin credential store (single admin)."""

    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)  # stored as plain or hashed

    def __str__(self):
        return self.username
