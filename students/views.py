# students/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from accounts.decorators import admin_or_supervisor_required
import json
import csv

from .models import Student
from .forms import StudentForm
from departments.models import Department, Supervisor, Course
from documents.models import Document
from reports.models import MonthlyReport

# ── PAGE VIEWS ──────────────────────────────────────────────────────────────

@login_required
def student_register(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    dept_filter = request.GET.get('dept', '')
    status_filter = request.GET.get('status', '')
    year_filter = request.GET.get('year', '')
    supervisor_filter = request.GET.get('supervisor', '')
    start_from = request.GET.get('start_from', '')
    start_to = request.GET.get('start_to', '')
    end_from = request.GET.get('end_from', '')
    end_to = request.GET.get('end_to', '')
    course_contains = request.GET.get('course', '')
    sort_by = request.GET.get('sort', 'name')
    
    # Base queryset
    students = Student.objects.select_related('department', 'supervisor', 'course')
    
    # Apply filters
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(course__name__icontains=search_query) |
            Q(supervisor__name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if dept_filter:
        students = students.filter(department_id=dept_filter)
    
    if status_filter:
        students = students.filter(status=status_filter.lower())
    
    if year_filter:
        students = students.filter(year_of_study=year_filter)
    
    if supervisor_filter:
        students = students.filter(supervisor_id=supervisor_filter)
    
    if start_from:
        students = students.filter(start_date__gte=start_from)
    
    if start_to:
        students = students.filter(start_date__lte=start_to)
    
    if end_from:
        students = students.filter(end_date__gte=end_from)
    
    if end_to:
        students = students.filter(end_date__lte=end_to)
    
    if course_contains:
        students = students.filter(course__name__icontains=course_contains)
    
    # Apply sorting
    sort_mappings = {
        'name': 'name',
        'name-desc': '-name',
        'start': 'start_date',
        'start-desc': '-start_date',
        'end': 'end_date',
        'end-desc': '-end_date',
    }
    
    if sort_by in sort_mappings:
        students = students.order_by(sort_mappings[sort_by])
    else:
        students = students.order_by('name')
    
    # Get filter options
    departments = Department.objects.all()
    supervisors = Supervisor.objects.filter(is_active=True)
    
    context = {
        'students': students,
        'departments': departments,
        'supervisors': supervisors,
        'filter_data': {
            'search': search_query,
            'dept': dept_filter,
            'status': status_filter,
            'year': year_filter,
            'supervisor': supervisor_filter,
            'start_from': start_from,
            'start_to': start_to,
            'end_from': end_from,
            'end_to': end_to,
            'course': course_contains,
            'sort': sort_by,
        }
    }
    
    return render(request, 'students/register.html', context)

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student.objects.select_related('department', 'supervisor', 'course'), id=student_id)
    documents = Document.objects.filter(student=student)
    reports = MonthlyReport.objects.filter(student=student).order_by('-month')
    
    context = {
        'student': student,
        'documents': documents,
        'reports': reports,
    }
    
    return render(request, 'students/detail.html', context)

@login_required
def students_by_dept(request):
    departments = Department.objects.prefetch_related('students__supervisor').all()
    
    context = {
        'departments': departments,
    }
    
    return render(request, 'students/by_dept.html', context)

@login_required
def students_timeline(request):
    students = Student.objects.select_related('department').all()
    
    context = {
        'students': students,
    }
    
    return render(request, 'students/timeline.html', context)

@login_required
def students_supervisors(request):
    supervisors = Supervisor.objects.prefetch_related('students').filter(is_active=True)
    
    context = {
        'supervisors': supervisors,
    }
    
    return render(request, 'students/supervisors.html', context)

@login_required
def export_index(request):
    students = Student.objects.select_related('department', 'supervisor', 'course').all()
    
    context = {
        'students': students,
    }
    
    return render(request, 'students/export.html', context)

# ── API VIEWS FOR AJAX ──────────────────────────────────────────────────────

@login_required
@require_GET
def student_api_detail(request, student_id):
    """Get student details for editing"""
    try:
        student = Student.objects.select_related('department', 'supervisor', 'course').get(id=student_id)
        data = {
            'success': True,
            'student': {
                'id': student.id,
                'student_id': student.student_id,
                'name': student.name,
                'contact': student.contact or '',
                'email': student.email or '',
                'emergency_contact': student.emergency_contact or '',
                'course': student.course.id if student.course else '',
                'course_name': student.course.name if student.course else '',
                'year_of_study': student.year_of_study,
                'department': student.department.id if student.department else '',
                'department_name': student.department.name if student.department else '',
                'supervisor': student.supervisor.id if student.supervisor else '',
                'supervisor_name': student.supervisor.name if student.supervisor else '',
                'supervisor_contact': student.supervisor.phone if student.supervisor else '',
                'start_date': student.start_date.isoformat() if student.start_date else '',
                'end_date': student.end_date.isoformat() if student.end_date else '',
                'status': student.status,
                'notes': student.notes or '',
            }
        }
        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Student not found'}, status=404)

@login_required
@admin_or_supervisor_required
def student_api_add(request):
    """Add a new student via AJAX"""
    
    try:
        mode = request.POST.get('mode', 'attachee')
        student_id = request.POST.get('student_id')
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        
        if not name or not department_id:
            return JsonResponse({
                'success': False, 
                'message': 'Name and Department are required.'
            })

        if mode == 'attachee' and not student_id:
            return JsonResponse({
                'success': False,
                'message': 'Student ID is required for attachees.'
            })

        if mode == 'intern' and not student_id:
            # generate a unique placeholder ID for interns
            base = f'INTERN-{int(timezone.now().timestamp())}'
            candidate = base
            count = 1
            while Student.objects.filter(student_id=candidate).exists():
                candidate = f'{base}-{count}'
                count += 1
            student_id = candidate
        
        # Check duplicate
        if Student.objects.filter(student_id=student_id).exists():
            return JsonResponse({
                'success': False, 
                'message': f'Student ID "{student_id}" already exists.'
            })
        
        # Get department
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Department not found.'})
        
        # Get supervisor (optional)
        supervisor_id = request.POST.get('supervisor')
        supervisor = None
        if supervisor_id:
            try:
                supervisor = Supervisor.objects.get(id=supervisor_id)
            except Supervisor.DoesNotExist:
                pass
        
        # Create student
        student = Student.objects.create(
            student_id=student_id,
            name=name,
            contact=request.POST.get('contact', ''),
            email=request.POST.get('email', ''),
            emergency_contact=request.POST.get('emergency_contact', ''),
            course=request.POST.get('course') or None,
            year_of_study=(request.POST.get('year_of_study') or None) if mode == 'attachee' else None,
            department=department,
            supervisor=supervisor,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            status=request.POST.get('status', 'active'),
            notes=request.POST.get('notes', '')
        )
        
        label = 'Intern' if mode == 'intern' else 'Attachee'
        return JsonResponse({
            'success': True, 
            'message': f'{label} {student.name} added successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error: {str(e)}'
        }, status=500)

@login_required
@admin_or_supervisor_required
def student_api_edit(request, student_id):
    """Edit an existing student via AJAX"""
    
    try:
        student = get_object_or_404(Student, id=student_id)
        
        student_id_new = request.POST.get('student_id')
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        
        if not student_id_new or not name or not department_id:
            return JsonResponse({
                'success': False, 
                'message': 'Student ID, Name, and Department are required.'
            })
        
        # Check duplicate
        if Student.objects.filter(student_id=student_id_new).exclude(id=student_id).exists():
            return JsonResponse({
                'success': False, 
                'message': f'Student ID "{student_id_new}" already exists.'
            })
        
        # Get department
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Department not found.'})
        
        # Get supervisor (optional)
        supervisor_id = request.POST.get('supervisor')
        supervisor = None
        if supervisor_id:
            try:
                supervisor = Supervisor.objects.get(id=supervisor_id)
            except Supervisor.DoesNotExist:
                pass
        
        # Update student
        student.student_id = student_id_new
        student.name = name
        student.contact = request.POST.get('contact', '')
        student.email = request.POST.get('email', '')
        student.emergency_contact = request.POST.get('emergency_contact', '')
        student.year_of_study = request.POST.get('year_of_study') or None
        student.department = department
        student.supervisor = supervisor
        student.start_date = request.POST.get('start_date')
        student.end_date = request.POST.get('end_date')
        student.status = request.POST.get('status', 'active')
        student.notes = request.POST.get('notes', '')
        student.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'{student.name} updated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error: {str(e)}'
        }, status=500)

@login_required
@admin_or_supervisor_required
def student_api_delete(request, student_id):
    """Delete a student via AJAX"""
    
    try:
        student = get_object_or_404(Student, id=student_id)
        name = student.name
        
        # Delete related documents
        Document.objects.filter(student=student).delete()
        
        # Delete related reports
        MonthlyReport.objects.filter(student=student).delete()
        
        # Delete student
        student.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'{name} deleted successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': f'Error: {str(e)}'
        }, status=500)

# ── EXPORT FUNCTIONS ──────────────────────────────────────────────────────

@login_required
def export_data(request):
    format_type = request.GET.get('format', 'csv')
    filtered_only = request.GET.get('filtered', 'false') == 'true'
    status_filter = request.GET.get('status', '')
    
    # Build queryset
    students = Student.objects.select_related('department', 'supervisor', 'course')
    
    if filtered_only:
        search_query = request.GET.get('search', '')
        if search_query:
            students = students.filter(
                Q(name__icontains=search_query) |
                Q(student_id__icontains=search_query) |
                Q(course__name__icontains=search_query)
            )
        dept_filter = request.GET.get('dept', '')
        if dept_filter:
            students = students.filter(department_id=dept_filter)
    
    if status_filter:
        students = students.filter(status=status_filter)
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="fsa_attachees_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Student ID', 'Full Name', 'Contact', 'Email', 
            'Emergency Contact', 'Course', 'Year', 'Department', 
            'Supervisor', 'Supervisor Contact', 'Start Date', 
            'End Date', 'Status', 'Notes'
        ])
        
        for student in students:
            writer.writerow([
                student.id,
                student.student_id,
                student.name,
                student.contact or '',
                student.email or '',
                student.emergency_contact or '',
                student.course.name if student.course else '',
                student.year_of_study or '',
                student.department.name,
                student.supervisor.name if student.supervisor else '',
                student.supervisor.phone if student.supervisor else '',
                student.start_date.isoformat() if student.start_date else '',
                student.end_date.isoformat() if student.end_date else '',
                student.get_status_display(),
                student.notes or '',
            ])
        
        return response
    elif format_type == 'xlsx':
        try:
            from openpyxl import Workbook
        except ImportError:
            return JsonResponse({'error': 'XLSX export requires openpyxl. Install it via requirements.'}, status=500)

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Attachees'

        headers = [
            'ID', 'Student ID', 'Full Name', 'Contact', 'Email',
            'Emergency Contact', 'Course', 'Year', 'Department',
            'Supervisor', 'Supervisor Contact', 'Start Date',
            'End Date', 'Status', 'Notes'
        ]
        sheet.append(headers)

        for student in students:
            sheet.append([
                student.id,
                student.student_id,
                student.name,
                student.contact or '',
                student.email or '',
                student.emergency_contact or '',
                student.course.name if student.course else '',
                student.year_of_study or '',
                student.department.name,
                student.supervisor.name if student.supervisor else '',
                student.supervisor.phone if student.supervisor else '',
                student.start_date.isoformat() if student.start_date else '',
                student.end_date.isoformat() if student.end_date else '',
                student.get_status_display(),
                student.notes or '',
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="fsa_attachees_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        workbook.save(response)
        return response
    elif format_type == 'json':
        data = []
        for student in students:
            data.append({
                'id': student.id,
                'student_id': student.student_id,
                'name': student.name,
                'contact': student.contact or '',
                'email': student.email or '',
                'emergency_contact': student.emergency_contact or '',
                'course': student.course.name if student.course else '',
                'year_of_study': student.year_of_study,
                'department': student.department.name,
                'supervisor': student.supervisor.name if student.supervisor else '',
                'supervisor_contact': student.supervisor.phone if student.supervisor else '',
                'start_date': student.start_date.isoformat() if student.start_date else '',
                'end_date': student.end_date.isoformat() if student.end_date else '',
                'status': student.status,
                'status_display': student.get_status_display(),
                'notes': student.notes or '',
            })
        
        return JsonResponse(data, safe=False)
    
    return JsonResponse({'error': 'Invalid format'}, status=400)