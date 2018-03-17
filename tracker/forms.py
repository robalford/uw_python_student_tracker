from django import forms

from .models import StudentTracker


class StudentTrackerForm(forms.ModelForm):
    class Meta:
        model = StudentTracker
        fields = [
            'student_tracking_csv',
            'grade_report_csv',
        ]
