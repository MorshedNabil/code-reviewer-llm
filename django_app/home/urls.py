from django.urls import path
from . import views

urlpatterns = [
    path('start_task/', views.start_task),
    path('task_status_view/<task_id>/', views.task_status_view),
]