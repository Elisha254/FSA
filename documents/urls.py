# documents/urls.py
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('upload/<int:student_id>/', views.document_upload, name='upload'),
    path('delete/<int:document_id>/', views.document_delete, name='delete'),
]