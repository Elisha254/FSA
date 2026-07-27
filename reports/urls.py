# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('student/<int:student_id>/', views.report_list, name='list'),
    path('create/<int:student_id>/', views.report_create, name='create'),
    path('edit/<int:report_id>/', views.report_edit, name='edit'),
    path('delete/<int:report_id>/', views.report_delete, name='delete'),
]