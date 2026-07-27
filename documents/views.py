# documents/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from students.models import Student
from accounts.decorators import admin_or_supervisor_required
from .models import Document
from .forms import DocumentForm

@login_required
@admin_or_supervisor_required
def document_upload(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = student
            document.save()
            return redirect('students:detail', student_id=student.id)
    else:
        form = DocumentForm()
    
    context = {
        'student': student,
        'form': form,
    }
    
    return render(request, 'documents/upload.html', context)

@login_required
@admin_or_supervisor_required
@require_POST
def document_delete(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    student_id = document.student.id
    document.delete()
    return JsonResponse({'success': True, 'message': 'Document deleted successfully'})