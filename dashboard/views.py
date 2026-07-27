# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from students.models import Student
from departments.models import Department, Supervisor
from reports.models import MonthlyReport
from documents.models import Document

@login_required
def dashboard_index(request):
    # Basic Statistics
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()
    completed_students = Student.objects.filter(status='completed').count()
    on_hold_students = Student.objects.filter(status='on_hold').count()
    withdrawn_students = Student.objects.filter(status='withdrawn').count()
    total_departments = Department.objects.count()
    total_supervisors = Supervisor.objects.count()
    total_reports = MonthlyReport.objects.count()
    total_documents = Document.objects.count()
    
    # Pending documents (students with any missing required upload types)
    pending_documents = Student.objects.annotate(
        passport_count=Count('documents', filter=Q(documents__document_type='passport')),
        student_id_count=Count('documents', filter=Q(documents__document_type='student_id')),
        university_letter_count=Count('documents', filter=Q(documents__document_type='university_letter')),
        acceptance_letter_count=Count('documents', filter=Q(documents__document_type='acceptance_letter')),
    ).filter(
        Q(passport_count=0) |
        Q(student_id_count=0) |
        Q(university_letter_count=0) |
        Q(acceptance_letter_count=0)
    ).count()
    
    # Students by Department
    dept_stats = Department.objects.annotate(
        student_count=Count('students')
    ).values('name', 'student_count').order_by('-student_count')
    
    # Students by Course
    course_stats = Student.objects.values('course__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Monthly Intake (last 12 months)
    monthly_intake = Student.objects.filter(
        submission_date__gte=timezone.now() - timedelta(days=365)
    ).annotate(
        month_name=TruncMonth('submission_date')
    ).values('month_name').annotate(
        count=Count('id')
    ).order_by('month_name')
    
    # Monthly Completion (last 12 months)
    monthly_completion = Student.objects.filter(
        end_date__gte=timezone.now() - timedelta(days=365),
        status='completed'
    ).annotate(
        month_name=TruncMonth('end_date')
    ).values('month_name').annotate(
        count=Count('id')
    ).order_by('month_name')
    
    # Supervisor Workload
    supervisor_workload = Supervisor.objects.annotate(
        student_count=Count('students')
    ).filter(student_count__gt=0).values('name', 'student_count').order_by('-student_count')[:10]
    
    # Document Completion Status
    document_status = {
        'passport': Student.objects.filter(documents__document_type='passport').count(),
        'student_id': Student.objects.filter(documents__document_type='student_id').count(),
        'university_letter': Student.objects.filter(documents__document_type='university_letter').count(),
        'acceptance_letter': Student.objects.filter(documents__document_type='acceptance_letter').count(),
    }
    
    # Monthly Report Submission
    report_submission = MonthlyReport.objects.filter(
        submitted_at__gte=timezone.now() - timedelta(days=365)
    ).annotate(
        month_name=TruncMonth('submitted_at')
    ).values('month_name').annotate(
        count=Count('id')
    ).order_by('month_name')
    
    # Lessons Learnt per Month
    lessons_submitted = MonthlyReport.objects.filter(
        submitted_at__gte=timezone.now() - timedelta(days=365)
    ).exclude(
        lessons_learnt__isnull=True
    ).exclude(
        lessons_learnt=''
    ).annotate(
        month_name=TruncMonth('submitted_at')
    ).values('month_name').annotate(
        count=Count('id')
    ).order_by('month_name')
    
    # Recent Students
    recent_students = Student.objects.select_related(
        'department', 'supervisor', 'course'
    ).order_by('-submission_date')[:5]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'completed_students': completed_students,
        'students_on_hold': on_hold_students,
        'students_withdrawn': withdrawn_students,
        'total_departments': total_departments,
        'total_supervisors': total_supervisors,
        'total_reports': total_reports,
        'total_documents': total_documents,
        'pending_documents': pending_documents,
        'dept_stats': dept_stats,
        'course_stats': course_stats,
        'monthly_intake': monthly_intake,
        'monthly_completion': monthly_completion,
        'supervisor_workload': supervisor_workload,
        'document_status': document_status,
        'report_submission': report_submission,
        'lessons_submitted': lessons_submitted,
        'recent_students': recent_students,
    }
    
    return render(request, 'dashboard/index.html', context)