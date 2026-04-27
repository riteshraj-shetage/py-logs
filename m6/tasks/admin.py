from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'created_by', 'created_at']
    list_filter = ['tenant']
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'tenant', 'status', 'priority', 'assignee', 'created_at']
    list_filter = ['status', 'priority', 'tenant']
    search_fields = ['title']
