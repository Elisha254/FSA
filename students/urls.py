# students/urls.py
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Page views
    path('register/', views.student_register, name='register'),
    path('detail/<int:student_id>/', views.student_detail, name='detail'),
    path('by-dept/', views.students_by_dept, name='by_dept'),
    path('timeline/', views.students_timeline, name='timeline'),
    path('supervisors/', views.students_supervisors, name='supervisors'),
    path('export/', views.export_index, name='export'),
    path('export/data/', views.export_data, name='export_data'),
    
    # API CRUD endpoints
    path('api/<int:student_id>/', views.student_api_detail, name='api_detail'),
    path('api/add/', views.student_api_add, name='api_add'),
    path('api/edit/<int:student_id>/', views.student_api_edit, name='api_edit'),
    path('api/delete/<int:student_id>/', views.student_api_delete, name='api_delete'),
]