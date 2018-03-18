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
            messages.error(request, 'Please correct the form errors below.')
            return redirect('create_report')
    student_tracker_form = StudentTrackerForm()
    context = {'student_tracker_form': student_tracker_form}
    return render(request, template_name='tracker/create_report.html', context=context)


def student_progress_report(request, pk):
    student_tracker = get_object_or_404(StudentTracker, pk=pk)
    student_tracker.update_student_progress()
    all_students = Student.objects.all()
    students_ahead = sorted(all_students.filter(progress_status=Student.AHEAD),
                            key=lambda s: s.num_completed_lessons, reverse=True)
    students_on_pace = sorted(all_students.filter(progress_status=Student.ON_PACE),
                              key=lambda s: s.num_completed_lessons, reverse=True)
    students_behind = sorted(all_students.filter(progress_status=Student.BEHIND),
                             key=lambda s: s.num_completed_lessons, reverse=True)
    students_no_progress = all_students.filter(progress_status=Student.NO_PROGRESS)
    number_active_students = all_students.filter(enrollment_status=Student.ACTIVE).count()
    percent_ahead_or_on_pace = ((len(students_ahead) + len(students_on_pace)) / number_active_students) * 100
    percent_behind = (len(students_behind) / number_active_students) * 100
    percent_no_progress = (len(students_no_progress) / number_active_students) * 100
    send_welcome_email = all_students.filter(welcome_email_sent=False)
    send_week1_email = []
    send_month1_email = []
    send_month2_email = []
    send_month3_email = []
    for student in all_students:
        if student.days_since_enrollment > 7 and student.num_completed_lessons == 0 and not student.month1_email_sent:
            send_week1_email.append(student)
        if student.days_since_enrollment > 30 and not student.month1_email_sent:
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
        'percent_ahead_or_on_pace': percent_ahead_or_on_pace,
        'percent_behind': percent_behind,
        'percent_no_progress': percent_no_progress,
        'send_welcome_email': send_welcome_email,
        'send_week1_email': send_week1_email,
        'send_month1_email': send_month1_email,
        'send_month2_email': send_month2_email,
        'send_month3_email': send_month3_email,
    }
    return render(request, template_name='tracker/progress_report.html', context=context)
