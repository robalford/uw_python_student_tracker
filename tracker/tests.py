import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from students.models import Student
from .models import StudentTracker


class StudentTrackerTestCase(TestCase):
    def setUp(self):
        # dynamically build enrollment dates relative to today, so output calculations and data don't change in test
        # over time
        today = datetime.date.today()
        days_enrolled = (56, 66, 69, 61, )
        enrollment_dates = []
        for amount in days_enrolled:
            start_date = today - datetime.timedelta(days=amount)
            end_date = start_date + datetime.timedelta(days=120)
            enrollment_dates.append(start_date.strftime('%m/%d/%y').replace('0', ''))
            enrollment_dates.append(end_date.strftime('%m/%d/%y').replace('0', ''))

        student_tracking_csv_data = """Last Name,First Name,Email Address,Enroll Date,Expiration Date,Grade Recorded,Recorded By,Date Final Grade Entered,Notes,,,,edx email
        Student1,Test,teststudent1@email.com,{},{},,,,"Welcome email sent, started course, behind at 1 month check in ",,,,
        Student2,Test,teststudent2@email.com,{},{},,,,"Welcome email sent, started course, behind at 1 month check in ",,,,
        Student3,Test,teststudent3@email.com,{},{},,,,"Welcome email sent, started course, on pace at 1 month check in",,,,
        Student4,Test,teststudent4@email.com,{},{},,,,"Welcome email sent, progress1 email sent, no assignments at 1 month check in",,,,
        Student5,Test,teststudent5@email.com,1/25/18,5/27/18,USC,Jane Woo,N/A,"Dropped Class. Welcome email sent, progress1 email sent, no assignments at 1 month check in",,,,
        """.format(*tuple(enrollment_dates))
        student_tracking_csv_data = student_tracking_csv_data.replace('\n        ', '\n').encode('iso-8859-15')

        grade_report_csv_data = b"""Student ID,Email,Username,Grade,Assignments 1: Lesson 2 Assignments,Assignments 2: Lesson 3 Assignments,Assignments 3: Lesson 4 Assignments,Assignments 4: Lesson 5 Assignments,Assignments 5: Lesson 6 Assignment,Assignments 6: Lesson 7 Assignment,Assignments 7: Lesson 8 Assignment,Assignments 8: Lesson 9 Assignment,Assignments 9: Lesson 10 Assignment,Assignments (Avg),Enrollment Track,Verification Status,Certificate Eligible,Certificate Delivered,Certificate Type
        382,teststudent1@email.com,TestStudent1,0.17,1.0,0.5,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,0.166666666667,no-id-professional,N/A,N,N,N/A
        386,teststudent2@email.com,TestStudent2,0.0,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,0.0,no-id-professional,N/A,N,N,N/A11,
        348,teststudent3@email.com,TestStudent3,0.78,1.0,1.0,1.0,1.0,1.0,1.0,1.0,Not Attempted,Not Attempted,0.777777777778,no-id-professional,N/A,N,N,N/A
        422,teststudent4@email.com,TestStudent4,0.04,0.333333333333,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,Not Attempted,0.037037037037,no-id-professional,N/A,N,N,N/A
        """

        student_tracking_file = SimpleUploadedFile('Tracking-Table1.csv', student_tracking_csv_data)
        grade_report_file = SimpleUploadedFile('Grade-Report.csv', grade_report_csv_data)
        student_tracker = StudentTracker(student_tracking_csv=student_tracking_file, grade_report_csv=grade_report_file)
        student_tracker.save()
        self.student_tracker = student_tracker

    # View tests

    def test_create_report(self):
        response = self.client.get(reverse('create_report'))
        self.assertContains(response, 'Upload a CSV version of the Python 210 SP Student Tracking file from the '
                                      'courseOneDrive account')

    def test_student_progress_report(self):
        response = self.client.get(reverse('progress_report', args=[self.student_tracker.pk]))
        # test that student data was saved to the db and rendered in the template
        for student in Student.objects.exclude(enrollment_status=Student.DROPPED_COURSE):
            self.assertContains(response, '{} ({})'.format(student.name, student.enrollment_email))
        self.assertContains(response, 'Student Progress Report')
        self.assertContains(response, '25% of students on pace to finish the course on time.')
        self.assertContains(response, '75% of students behind schedule to complete course.')
        self.assertContains(response, "<td>Test Student1 (teststudent1@email.com)</td>\n    <td>11.1% (1/9)</td>\n    "
                                      "<td>46.7% (56/120 days)</td>")
        self.assertContains(response, "<td>Test Student2 (teststudent2@email.com)</td>\n    <td>0% (0/9)</td>\n    "
                                      "<td>55.0% (66/120 days)</td>")
        self.assertContains(response, "<td>Test Student3 (teststudent3@email.com)</td>\n    <td>77.8% (7/9)</td>\n    "
                                      "<td>57.5% (69/120 days)</td>")
        self.assertContains(response, "<td>Test Student4 (teststudent4@email.com)</td>\n    <td>0% (0/9)</td>\n    "
                                      "<td>50.8% (61/120 days)</td>")
        self.assertNotContains(response, 'Test Student5')  # dropped course

    # Model method tests

    def test_update_student_progress(self):
        self.assertEqual(Student.objects.count(), 0)
        self.student_tracker.update_student_progress()
        self.assertEqual(Student.objects.count(), 5)
        # test student data against csv data
        student_ahead = Student.objects.get(enrollment_email='teststudent3@email.com')
        self.assertEqual(student_ahead.progress_status, Student.AHEAD)
        self.assertEqual(student_ahead.num_completed_lessons, 7)
        self.assertTrue(student_ahead.welcome_email_sent)
        self.assertTrue(student_ahead.month1_email_sent)
        student_behind = Student.objects.get(enrollment_email='teststudent1@email.com')
        self.assertEqual(student_behind.progress_status, Student.BEHIND)
        self.assertEqual(student_behind.num_completed_lessons, 1)
        self.assertTrue(student_behind.welcome_email_sent)
        self.assertTrue(student_behind.month1_email_sent)
        student_no_progress = Student.objects.get(enrollment_email='teststudent4@email.com')
        self.assertEqual(student_no_progress.progress_status, Student.BEHIND)
        self.assertEqual(student_no_progress.num_completed_lessons, 0)
        self.assertTrue(student_no_progress.welcome_email_sent)
        self.assertTrue(student_no_progress.month1_email_sent)
        student_dropped_course = Student.objects.get(enrollment_email='teststudent5@email.com')
        self.assertEqual(student_dropped_course.enrollment_status, Student.DROPPED_COURSE)
