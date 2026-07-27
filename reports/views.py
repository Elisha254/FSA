# reports/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from accounts.decorators import admin_or_supervisor_required
from .models import MonthlyReport
from students.models import Student
from .forms import MonthlyReportForm

@login_required
def report_list(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    reports = MonthlyReport.objects.filter(student=student).order_by('-month')
    
    context = {
        'student': student,
        'reports': reports,
    }
    
    return render(request, 'reports/list.html', context)

@login_required
@admin_or_supervisor_required
def report_create(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = MonthlyReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.student = student
            report.save()
            return redirect('reports:list', student_id=student.id)
    else:
        form = MonthlyReportForm()
    
    context = {
        'student': student,
        'form': form,
    }
    
    return render(request, 'reports/form.html', context)

@login_required
@admin_or_supervisor_required
def report_edit(request, report_id):
    report = get_object_or_404(MonthlyReport, id=report_id)
    
    if request.method == 'POST':
        form = MonthlyReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            return redirect('reports:list', student_id=report.student.id)
    else:
        form = MonthlyReportForm(instance=report)
    
    context = {
        'report': report,
        'form': form,
    }
    
    return render(request, 'reports/form.html', context)

@login_required
@admin_or_supervisor_required
@require_POST
def report_delete(request, report_id):
    report = get_object_or_404(MonthlyReport, id=report_id)
    student_id = report.student.id
    report.delete()
    return JsonResponse({'success': True, 'message': 'Report deleted successfully'})