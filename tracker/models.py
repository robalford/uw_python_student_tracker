from django.db import models


class StudentTracker(models.Model):
    student_tracking_csv = models.FileField(upload_to='tracking_files/')
    grade_report_csv = models.FileField(upload_to='tracking_files/')
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.date_recorded
