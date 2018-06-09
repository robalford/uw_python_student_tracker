from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from students.models import Student
from .forms import StudentTrackerForm
from .models import StudentTracker


def create_report(request):
    if request.method == 'POST':
        student_tracker_form = StudentTrackerForm(request.POST, request.FILES)
        if student_tracker_form.is_valid():
            student_tracker = student_tracker_form.save()
            return redirect('progress_report', pk=student_tracker.pk)
        else:
            messages.error(request, student_tracker_form.errors)
            return redirect('create_report')
    student_tracker_form = StudentTrackerForm()
    context = {'student_tracker_form': student_tracker_form}
    return render(request, template_name='tracker/create_report.html', context=context)


def sort_students_by_completed_lessons(students):
    """Helper to sort by the num_completed_lessons @property"""
    return sorted(students, key=lambda s: s.num_completed_lessons, reverse=True)


def student_progress_report(request, pk):
    student_tracker = get_object_or_404(StudentTracker, pk=pk)
    student_tracker.update_student_progress()
    active_students = Student.objects.filter(enrollment_status=Student.ACTIVE)
    # sort students into progress categories
    students_ahead = sort_students_by_completed_lessons(active_students.filter(progress_status=Student.AHEAD))
    students_on_pace = sort_students_by_completed_lessons(active_students.filter(progress_status=Student.ON_PACE))
    students_behind = sort_students_by_completed_lessons(active_students.filter(progress_status=Student.BEHIND))
    # separate students with no progress in the course
    students_no_progress = [
        student for student in active_students
        if not student.started_lessons
        and student not in students_on_pace
    ]
    students_behind = [student for student in students_behind if student not in students_no_progress]
    # calculate progress percentiles
    number_active_students = active_students.filter(enrollment_status=Student.ACTIVE).count()
    num_ahead_or_on_pace = len(students_ahead) + len(students_on_pace)
    percent_ahead_or_on_pace = (num_ahead_or_on_pace / number_active_students) * 100
    percent_behind = (len(students_behind) / number_active_students) * 100
    percent_no_progress = (len(students_no_progress) / number_active_students) * 100
    # build queries for inactive students
    inactive_students = Student.objects.exclude(enrollment_status=Student.ACTIVE)
    students_passed = sort_students_by_completed_lessons(
        inactive_students.filter(enrollment_status=Student.PASSED_COURSE))
    students_failed = sort_students_by_completed_lessons(
        inactive_students.filter(enrollment_status=Student.FAILED_COURSE))
    students_incomplete = sort_students_by_completed_lessons(
        inactive_students.filter(enrollment_status=Student.INCOMPLETE))
    students_dropped = sort_students_by_completed_lessons(
        inactive_students.filter(enrollment_status=Student.DROPPED_COURSE))
    number_inactive_students = inactive_students.count()
    percent_passed = (len(students_passed)/number_inactive_students) * 100
    percent_failed = (len(students_failed)/number_inactive_students) * 100
    percent_incomplete = (len(students_incomplete)/number_inactive_students) * 100
    percent_dropped = (len(students_dropped)/number_inactive_students) * 100
    # build lists of students for email check ins
    send_welcome_email = active_students.filter(welcome_email_sent=False)
    send_week1_email = []
    send_month1_email = []
    send_month2_email = []
    send_month3_email = []
    for student in active_students:
        if student.days_since_enrollment > 7 and student in students_no_progress \
                and not any([student.week1_email_sent,
                             student.month1_email_sent,
                             student.month2_email_sent,
                             student.month3_email_sent]):
            send_week1_email.append(student)
        if student.days_since_enrollment >= 30 and not student.month1_email_sent:
            send_month1_email.append(student)
        if student.days_since_enrollment > 60 and not student.month2_email_sent:
            send_month2_email.append(student)
        if student.days_since_enrollment > 90 and not student.month3_email_sent:
            send_month3_email.append(student)
    context = {
        'students_ahead': students_ahead,
        'students_on_pace': students_on_pace,
        'students_behind': students_behind,
        'students_no_progress': students_no_progress,
        'number_active_students': number_active_students,
        'num_ahead_or_on_pace': num_ahead_or_on_pace,
        'percent_ahead_or_on_pace': percent_ahead_or_on_pace,
        'percent_behind': percent_behind,
        'percent_no_progress': percent_no_progress,
        'students_passed': students_passed,
        'students_failed': students_failed,
        'students_incomplete': students_incomplete,
        'students_dropped': students_dropped,
        'number_inactive_students': number_inactive_students,
        'percent_passed': percent_passed,
        'percent_failed': percent_failed,
        'percent_incomplete': percent_incomplete,
        'percent_dropped': percent_dropped,
        'send_welcome_email': send_welcome_email,
        'send_week1_email': send_week1_email,
        'send_month1_email': send_month1_email,
        'send_month2_email': send_month2_email,
        'send_month3_email': send_month3_email,
    }
    return render(request, template_name='tracker/progress_report.html', context=context)


def send_welcome_email(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == 'POST':
        student.welcome_email_sent = True
        student.save()
        return redirect('progress_report', pk=StudentTracker.objects.latest('date_recorded').pk)
    context = {'student': student}
    return render(request, template_name='tracker/welcome_email.html', context=context)


def send_one_week_check_in(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == 'POST':
        student.week1_email_sent = True
        student.save()
        return redirect('progress_report', pk=StudentTracker.objects.latest('date_recorded').pk)
    context = {'student': student}
    return render(request, template_name='tracker/one_week_email.html', context=context)


def send_monthly_checkin(request, student_pk, month_completed):
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == 'POST':
        setattr(student, 'month{}_email_sent'.format(month_completed), True)
        student.save()
        return redirect('progress_report', pk=StudentTracker.objects.latest('date_recorded').pk)
    context = {
        'student': student,
        'month_completed': month_completed,
    }
    finish_lesson_by_month = (('3', '1'), ('5', '2'), ('8', '3'))
    for lesson, month in finish_lesson_by_month:
        if str(month_completed) == month:
            if getattr(student, 'lesson{}_score'.format(lesson)) != 1.0:
                context['on_pace_to_finish'] = False
            else:
                context['on_pace_to_finish'] = True
            context['lesson_number'] = lesson
    return render(request, template_name='tracker/monthly_email.html', context=context)
