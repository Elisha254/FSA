# reports/models.py
from django.db import models
from students.models import Student

class MonthlyReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reports')
    month = models.DateField()
    activities = models.TextField()
    accomplishments = models.TextField()
    challenges = models.TextField(blank=True, null=True)
    lessons_learnt = models.TextField(blank=True, null=True)
    supervisor_remarks = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.month.strftime('%B %Y')}"
    
    def month_name(self):
        return self.month.strftime('%B %Y')
    
    class Meta:
        ordering = ['-month', '-submitted_at']
        unique_together = ['student', 'month']