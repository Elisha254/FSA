# students/admin.py
from django.contrib import admin
from .models import Student
from departments.models import Department, Course, Supervisor
from documents.models import Document
from reports.models import MonthlyReport

class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'student_id', 'department', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'department', 'year_of_study']
    search_fields = ['name', 'student_id', 'email', 'contact']
    readonly_fields = ['submission_date', 'created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('student_id', 'name', 'contact', 'email', 'emergency_contact')
        }),
        ('Academic Information', {
            'fields': ('course', 'year_of_study', 'department')
        }),
        ('Attachment Information', {
            'fields': ('supervisor', 'start_date', 'end_date', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes', 'submission_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    search_fields = ['name']

class SupervisorAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'email', 'phone', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'email']

class DocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'document_type', 'uploaded_at']
    list_filter = ['document_type']
    search_fields = ['student__name', 'student__student_id']

class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'month', 'submitted_at']
    list_filter = ['month']
    search_fields = ['student__name', 'student__student_id']

admin.site.register(Student, StudentAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Supervisor, SupervisorAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(MonthlyReport, MonthlyReportAdmin)