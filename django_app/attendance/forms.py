from django import forms
from .models import Student


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Admin Username",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
            }
        )
    )


class AddStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_id", "name", "email", "department"]
        widgets = {
            "student_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 12410248",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Full Name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "student@example.com",
                }
            ),
            "department": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. MCA, BCA",
                }
            ),
        }
