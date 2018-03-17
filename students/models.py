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
    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (DROPPED_COURSE, 'Dropped'),
        (PASSED_COURSE, 'Passed course'),
        (FAILED_COURSE, 'Failed course'),
    )
    enrollment_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=ACTIVE)
    edx_id = models.IntegerField()
    edx_email = models.EmailField()
    edx_username = models.CharField(max_length=50)
    lesson2_score = models.DecimalField(max_digits=3, decimal_places=2)
    lesson3_score = models.DecimalField(max_digits=3, decimal_places=2)
    lesson4_score = models.DecimalField(max_digits=3, decimal_places=2)
    lesson5_score = models.DecimalField(max_digits=3, decimal_places=2)
    lesson6_score = models.DecimalField(max_digits=3, decimal_places=2)
    lesson7_score = models.DecimalField(max_digits=3, decimal_places=2)
    lesson8_score = models.DecimalField(max_digits=3, decimal_places=2)
    lesson9_score = models.DecimalField(max_digits=3, decimal_places=2)
    lesson10_score = models.DecimalField(max_digits=3, decimal_places=2)
    welcome_email_sent = models.BooleanField(default=False)
    week1_email_sent = models.BooleanField(default=False)
    month1_email_sent = models.BooleanField(default=False)
    month2_email_sent = models.BooleanField(default=False)
    month3_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.name


