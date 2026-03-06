# task_manager_frontend/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Authentication Routes
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Task Action Routes (CRUD)
    # The <int:pk> allows us to pass the specific ID of the task to the backend
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('toggle/<int:pk>/', views.toggle_task, name='toggle_task'),
]