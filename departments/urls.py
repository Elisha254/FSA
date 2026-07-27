# departments/urls.py
from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('list/', views.department_list, name='list'),
    
    # API CRUD endpoints
    path('api/add/', views.department_add_ajax, name='api_add'),
    path('api/edit/<int:department_id>/', views.department_edit_ajax, name='api_edit'),
    path('api/delete/<int:department_id>/', views.department_delete_ajax, name='api_delete'),
    path('api/supervisor/add/', views.supervisor_add_ajax, name='supervisor_add'),
    path('api/supervisor/edit/<int:supervisor_id>/', views.supervisor_edit_ajax, name='supervisor_edit'),
    path('api/supervisor/delete/<int:supervisor_id>/', views.supervisor_delete_ajax, name='supervisor_delete'),
    path('api/supervisors/', views.supervisor_list_ajax, name='supervisor_list'),
    path('api/courses/', views.course_list_ajax, name='course_list'),
]