import csv
import datetime
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

    def update_student_progress(self):
        student_tracking_dict = self.convert_csv_to_dict(self.student_tracking_csv)
        # convert grade report to dict with emails as keys
        grade_report_dict = {student['Email']: student for student in self.convert_csv_to_dict(self.grade_report_csv)}
        for student_data in student_tracking_dict:
            student, _ = Student.objects.get_or_create(
                name='{} {}'.format(student_data['First Name'], student_data['First Name']),
                enrollment_email=student_data['Email'],
                enrollment_date=self.format_date_from_spreadsheet(student_data['Enroll Date']),
                course_end_date=self.format_date_from_spreadsheet(student_data['Expiration Date'])
            )
            grade_report_data = grade_report_dict.get(student.enrollment_email)
            if grade_report_data:
                student.update(
                    edx_id=grade_report_data['Student ID'],
                    edx_email=grade_report_data['Email'],
                    edx_username=grade_report_data['Username'],
                    lesson2_score=grade_report_data['Assignments 1: Lesson 2 Assignments'],
                    lesson3_score=grade_report_data['Assignments 2: Lesson 3 Assignments'],
                    lesson4_score=grade_report_data['Assignments 3: Lesson 4 Assignments'],
                    lesson5_score=grade_report_data['Assignments 4: Lesson 5 Assignments'],
                    lesson6_score=grade_report_data['Assignments 5: Lesson 6 Assignments'],
                    lesson7_score=grade_report_data['Assignments 6: Lesson 7 Assignments'],
                    lesson8_score=grade_report_data['Assignments 7: Lesson 8 Assignments'],
                    lesson9_score=grade_report_data['Assignments 8: Lesson 9 Assignments'],
                    lesson10_score=grade_report_data['Assignments 9: Lesson 10 Assignments']
                )
            # update student progress field
            if not student.completed_lessons:
                student.progress_status = Student.NO_PROGRESS
            elif (student.percent_of_enrollment_period_completed - student.percent_assignments_completed) <= -10:
                student.progress_status = Student.AHEAD
            elif 10 >= (student.percent_of_enrollment_period_completed - student.percent_assignments_completed) > -10:
                student.progress_status = Student.ON_PACE
            else:
                student.progress_status = Student.BEHIND
            student.save()









