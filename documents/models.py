# documents/models.py
from django.db import models
from students.models import Student

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('passport', 'Passport Photo'),
        ('student_id', 'Student ID Copy'),
        ('university_letter', 'University Application Letter'),
        ('acceptance_letter', 'FSA Acceptance Letter'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)

    def document_upload_path(instance, filename):
        folder_map = {
            'passport': 'passport_photos',
            'student_id': 'student_ids',
            'university_letter': 'application_letters',
            'acceptance_letter': 'acceptance_letters',
        }
        folder = folder_map.get(instance.document_type, 'documents')
        return f'{folder}/{instance.student.student_id}/{filename}'

    file = models.FileField(upload_to=document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.get_document_type_display()}"
    
    def filename(self):
        return self.file.name.split('/')[-1]
    
    class Meta:
        ordering = ['-uploaded_at']
        unique_together = ['student', 'document_type']