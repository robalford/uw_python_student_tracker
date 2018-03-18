import csv
import datetime
from decimal import Decimal
import io

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
        return datetime.datetime(int('20' + split_date[2]), int(split_date[0]), int(split_date[1]))
    
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
                name='{} {}'.format(student_data['First Name'], student_data['Last Name']),
                enrollment_email=student_data['Email Address'],
                enrollment_date=self.format_date_from_spreadsheet(student_data['Enroll Date']),
                course_end_date=self.format_date_from_spreadsheet(student_data['Expiration Date'])
            )
            if 'Welcome email sent' in student_data['Notes']:
                student.welcome_email_sent = True
            if 'progress1 email sent' in student_data['Notes']:
                student.week1_email_sent = True
            if '1 month check in' in student_data['Notes']:
                student.month1_email_sent = True
            grade_report_data = grade_report_dict.get(student.enrollment_email)
            if grade_report_data:
                student.edx_id = grade_report_data['Student ID']
                student.edx_email = grade_report_data['Email']
                student.edx_username = grade_report_data['Username']
                student.lesson2_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 1: Lesson 2 Assignments'])
                student.lesson3_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 2: Lesson 3 Assignments'])
                student.lesson4_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 3: Lesson 4 Assignments'])
                student.lesson5_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 4: Lesson 5 Assignments'])
                student.lesson6_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 5: Lesson 6 Assignment'])
                student.lesson7_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 6: Lesson 7 Assignment'])
                student.lesson8_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 7: Lesson 8 Assignment'])
                student.lesson9_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 8: Lesson 9 Assignment'])
                student.lesson10_score = self.convert_score_to_decimal(
                    grade_report_data['Assignments 9: Lesson 10 Assignment'])
                student.save()
            # update student progress field
            student.update_progress_status()









