from django.urls import path
from . import views

urlpatterns = [
    path('',              views.task_list,    name='task-list'),
    path('<int:pk>/',     views.task_detail,  name='task-detail'),
    path('<int:pk>/reorder/', views.task_reorder, name='task-reorder'),
]