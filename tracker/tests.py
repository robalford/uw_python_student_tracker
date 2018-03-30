from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from students.models import Student
from .models import StudentTracker

STUDENT_TRACKING_CSV_DATA = b"""Last Name,First Name,Email Address,Enroll Date,Expiration Date,Grade Recorded,Recorded By,Date Final Grade Entered,Notes,,,,edx email
Fake,Student,fake@student.com,2/7/18,6/9/18,,,,"Welcome email sent, started course, on pace at 1 month check in",,,,
Imaginary,Student2,fake@student2.com,1/25/18,5/27/18,USC,Fake Admin,N/A,"Dropped Class. Welcome email sent, progress1 email sent, no assignments at 1 month check in",,,,
Another,Fake Student,test@123.com,3/13/18,7/11/18,,,,Welcome email sent,,,,
Totally,Fake,totally@fake.com,1/25/18,5/27/18,,,,"Welcome email sent, started course, behind at 1 month check in ",,,,
Not,Real,not@real.net,1/30/18,6/1/18,,,,"Welcome email sent, progress1 email sent, no assignments at 1 month check in",,,,
"""

GRADE_REPORT_CSV_DATA = b"""Student ID,Email,Username,Grade,Assignments 1: Lesson 2 Assignments,Assignments 2: Lesson 3 Assignments,Assignments 3: Lesson 4 Assignments,Assignments 4: Lesson 5 Assignments,Assignments 5: Lesson 6 Assignment,Assignments 6: Lesson 7 Assignment,Assignments 7: Lesson 8 Assignment,Assignments 8: Lesson 9 Assignment,Assignments 9: Lesson 10 Assignment,Assignments (Avg),Enrollment Track,Verification Status,Certificate Eligible,Certificate Delivered,Certificate Type
9,fake@student.com,FakeUser,0.0,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,0.0,no-id-professional,N/A,N,N,N/A
17,fake@student2.com,FakeUser2,0.67,1.0,1.0,1.0,1.0,1.0,1.0,Not Attempted,Not Attempted,Not Attempted,0.666666666667,no-id-professional,N/A,N,N,N/A
11,test@123.com,FakeUser3,0.56,1.0,1.0,1.0,1.0,1.0,Not Attempted,Not Attempted,Not Attempted,Not Attempted,0.555555555556,no-id-professional,N/A,N,N,N/A
303,totally@fake.com,FakeUser4,0.27,1.0,1.0,0.444444444444,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,0.271604938272,no-id-professional,N/A,N,N,N/A
114,not@real.net,FakeUser5,0.0,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,0.0,no-id-professional,N/A,N,N,N/A
"""


class StudentTrackerTestCase(TestCase):
    def setUp(self):
        student_tracking_file = SimpleUploadedFile('Tracking-Table1.csv', STUDENT_TRACKING_CSV_DATA)
        grade_report_file = SimpleUploadedFile('Grade-Report.csv', GRADE_REPORT_CSV_DATA)
        student_tracker = StudentTracker(student_tracking_csv=student_tracking_file, grade_report_csv=grade_report_file)
        student_tracker.save()
        self.student_tracker = student_tracker

    def test_create_report(self):
        response = self.client.get(reverse('create_report'))
        self.assertContains(response, 'Upload a CSV version of the Python 210 SP Student Tracking file from the '
                                      'courseOneDrive account')

    def test_student_progress_report(self):
        response = self.client.get(reverse('progress_report', args=[self.student_tracker.pk]))
        self.assertContains(response, 'Student Progress Report')
        self.assertContains(response, '25% of students on pace to finish the course on time.')
        self.assertContains(response, '75% of students behind schedule to complete course.')
        # test that student data was saved to the db and rendered in the template
        for student in Student.objects.exclude(enrollment_status=Student.DROPPED_COURSE):
            self.assertContains(response, '{} ({})'.format(student.name, student.enrollment_email))


