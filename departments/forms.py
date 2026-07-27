# departments/forms.py
from django import forms
from .models import Department, Supervisor, Course

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SupervisorForm(forms.ModelForm):
    class Meta:
        model = Supervisor
        fields = ['name', 'email', 'phone', 'department', 'is_active']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'department', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }