from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('start_task/', views.start_task, name='start_task'),
    path('task_status_view/<task_id>/', views.task_status_view, name='task_status_view'),
]