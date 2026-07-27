# departments/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django.db.models import Count
from accounts.decorators import admin_or_supervisor_required
from .models import Department, Supervisor, Course
from .forms import DepartmentForm, SupervisorForm, CourseForm

@login_required
def department_list(request):
    departments = Department.objects.all().annotate(
        student_count=Count('students'),
        supervisor_count=Count('supervisors')
    )
    supervisors = Supervisor.objects.select_related('department').all()
    
    context = {
        'departments': departments,
        'supervisors': supervisors,
    }
    
    return render(request, 'departments/list.html', context)

@login_required
@admin_or_supervisor_required
def department_add_ajax(request):
    """Add a new department via AJAX"""
    
    try:
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if not name:
            return JsonResponse({'success': False, 'message': 'Department name is required.'})
        
        if Department.objects.filter(name=name).exists():
            return JsonResponse({'success': False, 'message': f'Department "{name}" already exists.'})
        
        department = Department.objects.create(
            name=name,
            description=description
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Department "{department.name}" added successfully!',
            'department': {
                'id': department.id,
                'name': department.name
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@admin_or_supervisor_required
def supervisor_add_ajax(request):
    """Add a new supervisor via AJAX"""
    
    try:
        name = request.POST.get('name')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        department_id = request.POST.get('department')
        
        if not name or not department_id:
            return JsonResponse({'success': False, 'message': 'Name and Department are required.'})
        
        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Department not found.'})
        
        supervisor = Supervisor.objects.create(
            name=name,
            email=email,
            phone=phone,
            department=department,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Supervisor "{supervisor.name}" added successfully!',
            'supervisor': {
                'id': supervisor.id,
                'name': supervisor.name
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@admin_or_supervisor_required
def department_edit_ajax(request, department_id):
    try:
        department = get_object_or_404(Department, id=department_id)
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        if not name:
            return JsonResponse({'success': False, 'message': 'Department name is required.'})

        if Department.objects.filter(name=name).exclude(id=department_id).exists():
            return JsonResponse({'success': False, 'message': f'Department "{name}" already exists.'})

        department.name = name
        department.description = description
        department.save()

        return JsonResponse({'success': True, 'message': f'Department "{department.name}" updated successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@admin_or_supervisor_required
def department_delete_ajax(request, department_id):
    try:
        department = get_object_or_404(Department, id=department_id)
        department.delete()
        return JsonResponse({'success': True, 'message': f'Department "{department.name}" deleted successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@admin_or_supervisor_required
def supervisor_edit_ajax(request, supervisor_id):
    try:
        supervisor = get_object_or_404(Supervisor, id=supervisor_id)
        name = request.POST.get('name')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        department_id = request.POST.get('department')
        is_active = request.POST.get('is_active') == 'true'

        if not name or not department_id:
            return JsonResponse({'success': False, 'message': 'Name and Department are required.'})

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Department not found.'})

        supervisor.name = name
        supervisor.email = email
        supervisor.phone = phone
        supervisor.department = department
        supervisor.is_active = is_active
        supervisor.save()

        return JsonResponse({'success': True, 'message': f'Supervisor "{supervisor.name}" updated successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@admin_or_supervisor_required
def supervisor_delete_ajax(request, supervisor_id):
    try:
        supervisor = get_object_or_404(Supervisor, id=supervisor_id)
        supervisor.delete()
        return JsonResponse({'success': True, 'message': f'Supervisor "{supervisor.name}" deleted successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@login_required
@require_GET
def supervisor_list_ajax(request):
    """Get list of supervisors for dropdown"""
    department_id = request.GET.get('department')
    supervisors = Supervisor.objects.filter(is_active=True)
    
    if department_id:
        supervisors = supervisors.filter(department_id=department_id)
    
    data = [
        {'id': s.id, 'name': s.name, 'phone': s.phone or ''}
        for s in supervisors.order_by('name')
    ]
    
    return JsonResponse({'success': True, 'supervisors': data})

@login_required
@require_GET
def course_list_ajax(request):
    """Get list of courses for dropdown"""
    department_id = request.GET.get('department')
    courses = Course.objects.all()
    
    if department_id:
        courses = courses.filter(department_id=department_id)
    
    data = [
        {'id': c.id, 'name': c.name}
        for c in courses.order_by('name')
    ]
    
    return JsonResponse({'success': True, 'courses': data})