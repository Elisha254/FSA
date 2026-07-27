# documents/forms.py
from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5MB.')
            
            # Validate file extension
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('File must be PDF, JPG, or PNG format.')
        
        return file