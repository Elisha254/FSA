# reports/forms.py
from datetime import timezone
from django import forms
from .models import MonthlyReport


class MonthlyReportForm(forms.ModelForm):
    class Meta:
        model = MonthlyReport
        fields = ['month', 'activities', 'accomplishments', 'challenges', 'lessons_learnt', 'supervisor_remarks']
        widgets = {
            'month': forms.DateInput(attrs={'type': 'month'}),
            'activities': forms.Textarea(attrs={'rows': 4}),
            'accomplishments': forms.Textarea(attrs={'rows': 4}),
            'challenges': forms.Textarea(attrs={'rows': 3}),
            'lessons_learnt': forms.Textarea(attrs={'rows': 3}),
            'supervisor_remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_month(self):
        month = self.cleaned_data.get('month')
        if month and month > timezone.now().date():
            raise forms.ValidationError('Cannot submit report for a future month.')
        return month