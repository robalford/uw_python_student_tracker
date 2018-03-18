import datetime

from django.db import models


class Student(models.Model):
    name = models.CharField(max_length=100)
    enrollment_email = models.EmailField()
    enrollment_date = models.DateField()
    course_end_date = models.DateField()
    ACTIVE = 'A'
    DROPPED_COURSE = 'D'
    PASSED_COURSE = 'P'
    FAILED_COURSE = 'F'
    ENROLLMENT_STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (DROPPED_COURSE, 'Dropped'),
        (PASSED_COURSE, 'Passed course'),
        (FAILED_COURSE, 'Failed course'),
    )
    enrollment_status = models.CharField(max_length=1, choices=ENROLLMENT_STATUS_CHOICES, default=ACTIVE)
    edx_id = models.IntegerField(null=True, blank=True)
    edx_email = models.EmailField(blank=True)
    edx_username = models.CharField(max_length=50, blank=True)
    lesson2_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    lesson3_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    lesson4_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    lesson5_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    lesson6_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    lesson7_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    lesson8_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    lesson9_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    lesson10_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    BEHIND = 'B'
    ON_PACE = 'O'
    AHEAD = 'A'
    NO_PROGRESS = 'N'
    PROGRESS_STATUS_CHOICES = (
        (BEHIND, 'Behind schedule'),
        (ON_PACE, 'On pace'),
        (AHEAD, 'Ahead of schedule'),
        (NO_PROGRESS, 'No progress'),
    )
    progress_status = models.CharField(max_length=1, choices=PROGRESS_STATUS_CHOICES, default=NO_PROGRESS)
    welcome_email_sent = models.BooleanField(default=False)
    week1_email_sent = models.BooleanField(default=False)
    month1_email_sent = models.BooleanField(default=False)
    month2_email_sent = models.BooleanField(default=False)
    month3_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @classmethod
    def grade_score_fields(cls):
        return [
            'lesson2_score',
            'lesson3_score',
            'lesson4_score',
            'lesson5_score',
            'lesson6_score',
            'lesson7_score',
            'lesson8_score',
            'lesson9_score',
            'lesson10_score',
        ]

    @property
    def completed_lessons(self):
        return [field for field in self.grade_score_fields() if getattr(self, field) == 1.0]

    @property
    def num_completed_lessons(self):
        return len(self.completed_lessons)

    @property
    def percent_assignments_completed(self):
        return (len(self.completed_lessons) / 9) * 100

    @property
    def days_since_enrollment(self):
        return (datetime.date.today() - self.enrollment_date).days

    @property
    def percent_of_enrollment_period_completed(self):
        return (self.days_since_enrollment / 120) * 100

    def update_progress_status(self):
        if not self.completed_lessons:
            self.progress_status = Student.NO_PROGRESS
        elif (self.percent_of_enrollment_period_completed - self.percent_assignments_completed) <= -5:
            self.progress_status = Student.AHEAD
        elif 15 >= (self.percent_of_enrollment_period_completed - self.percent_assignments_completed) > -15:
            self.progress_status = Student.ON_PACE
        else:
            self.progress_status = Student.BEHIND
        self.save()


