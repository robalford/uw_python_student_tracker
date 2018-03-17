from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from students.models import Student
from .forms import StudentTrackerForm
from .models import StudentTracker


def create_report(request):
    if request.method == 'POST':
        student_tracker_form = StudentTrackerForm(request.POST)
        if student_tracker_form.is_valid():
            student_tracker = student_tracker_form.save()
            return redirect('tracker:student_progress_report', pk=student_tracker.pk)
        else:
            messages.error(request, 'Please correct the form errors below.')
            return redirect('tracker:create_report')
    student_tracker_form = StudentTrackerForm()
    context = {'student_tracker_form': student_tracker_form}
    return render(request, template_name='tracker/create_report.html', context=context)


def student_progress_report(request, pk):
    student_tracker = get_object_or_404(StudentTracker, pk=pk)
    student_tracker.update_student_progress()
    all_students = Student.objects.all()
    students_ahead = all_students.filter(progress_status=Student.AHEAD)
    students_on_pace = all_students.filter(progress_status=Student.ON_PACE)
    students_behind = all_students.filter(progress_status=Student.BEHIND)
    students_no_progress = all_students.filter(progress_status=Student.NO_PROGRESS)
    number_active_students = all_students.filter(enrollment_status=Student.ACTIVE).count()
    percent_ahead_or_on_pace = ((students_ahead.count() + students_on_pace.count()) / number_active_students) * 100
    percent_behind = (students_behind / number_active_students) * 100
    percent_no_progress = (students_no_progress / number_active_students) * 100
    context = {
        'students_ahead': students_ahead,
        'students_on_pace': students_on_pace,
        'students_behind': students_behind,
        'students_no_progress': students_no_progress,
        'number_active_students': number_active_students,
        'percent_ahead_or_on_pace': percent_ahead_or_on_pace,
        'percent_behind': percent_behind,
        'percent_no_progress': percent_no_progress,
    }
    return render(request, template_name='tracker/progress_report.html', context=context)
