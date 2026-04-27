from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list_view, name='project_list'),
    path('create/', views.project_create_view, name='project_create'),
    path('<int:pk>/', views.project_detail_view, name='project_detail'),
    path('tasks/create/', views.task_create_view, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_update_view, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete_view, name='task_delete'),
]
