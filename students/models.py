# students/models.py
from django.db import models
from django.utils import timezone
from departments.models import Department, Course, Supervisor

class Student(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('withdrawn', 'Withdrawn'),
    )
    
    student_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    year_of_study = models.PositiveSmallIntegerField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def days_remaining(self):
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return max(delta.days, 0)
        return None
    
    def days_elapsed(self):
        if self.start_date:
            delta = timezone.now().date() - self.start_date
            return max(delta.days, 0)
        return None
    
    def attachment_duration(self):
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return delta.days
        return None
    
    class Meta:
        ordering = ['-submission_date']