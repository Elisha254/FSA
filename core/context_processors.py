# core/context_processors.py
from departments.models import Department
from django.utils import timezone

def site_processors(request):
    return {
        'departments': Department.objects.all(),
        'current_date': timezone.now(),
    }