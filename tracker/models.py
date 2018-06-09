import csv
import datetime
from decimal import Decimal
import io
from itertools import islice

from django.db import models

from students.models import Student


class StudentTracker(models.Model):
    student_tracking_csv = models.FileField(upload_to='tracking_files/')
    grade_report_csv = models.FileField(upload_to='tracking_files/')
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.date_recorded

    @staticmethod
    def convert_csv_to_dict(file):
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        file_as_dict = csv.DictReader(io_string)
        return file_as_dict

    @staticmethod
    def format_date_from_spreadsheet(date):
        split_date = date.split('/')
        return datetime.date(int('20' + split_date[2]), int(split_date[0]), int(split_date[1]))
    
    @staticmethod
    def convert_score_to_decimal(score):
        if score == 'Not Attempted':
            score = '0.0'
        return Decimal(score)

    def update_student_progress(self):
        student_tracking_dict = self.convert_csv_to_dict(self.student_tracking_csv)
        # convert grade report to dict with emails as keys
        grade_report_dict = {student['Email']: student for student in self.convert_csv_to_dict(self.grade_report_csv)}
        for student_data in student_tracking_dict:
            if not any(student_data.values()):  # skip empty rows
                continue
            student, _ = Student.objects.get_or_create(
                name='{} {}'.format(student_data['First Name'].strip(), student_data['Last Name'].strip()),
                enrollment_email=student_data['Email Address'].strip(),
                enrollment_date=self.format_date_from_spreadsheet(student_data['Enroll Date'].strip()),
                course_end_date=self.format_date_from_spreadsheet(student_data['Expiration Date'].strip())
            )

            # update email booleans based on notes
            if 'Welcome email sent' in student_data['Notes']:
                student.welcome_email_sent = True
            if 'progress1 email sent' in student_data['Notes']:
                student.week1_email_sent = True
            if '1 month check in' in student_data['Notes']:
                student.month1_email_sent = True
            if '2 month check in sent' in student_data['Notes']:
                student.month2_email_sent = True

            # update status (this could be handled more elegantly if you changed the enrollment_status field to use
            # the actual status codes)
            if 'Dropped' in student_data['Notes'] or student_data['Date Final Grade Entered'].strip() == 'N/A':
                student.enrollment_status = Student.DROPPED_COURSE
            elif student_data['Grade Recorded'].strip() == 'USC':
                student.enrollment_status = Student.FAILED_COURSE
            elif student_data['Grade Recorded'].strip() == 'SC':
                student.enrollment_status = Student.PASSED_COURSE
            elif student_data['Grade Recorded'].strip() == 'Incomplete':
                student.enrollment_status = Student.INCOMPLETE

            # if student uses a different email for edx, use that for grade report lookup
            if student.edx_email:
                grade_report_data = grade_report_dict.get(student.edx_email)
            else:
                grade_report_data = grade_report_dict.get(student.enrollment_email)

            # update grade data
            if grade_report_data:
                student.edx_id = grade_report_data['Student ID']
                student.edx_email = grade_report_data['Email']
                student.edx_username = grade_report_data['Username']
                # list of tuples with lesson model fields and lesson keys from grade_report dict for updating grade data
                lesson_fields_and_assignments = zip(Student.grade_score_fields(),
                                                    islice(grade_report_data.keys(), 4, 13))
                for field, assignment in lesson_fields_and_assignments:
                    setattr(student, field, self.convert_score_to_decimal(grade_report_data[assignment]))
                student.save()
            # update student progress field
            student.update_progress_status()









