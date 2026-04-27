from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Task
from .forms import ProjectForm, TaskForm


@login_required
def project_list_view(request):
    tenant = request.tenant
    if not tenant:
        messages.warning(request, 'You need to be part of an organization first.')
        return redirect('register_org')
    projects = Project.objects.filter(tenant=tenant)
    return render(request, 'tasks/project_list.html', {'projects': projects, 'tenant': tenant})


@login_required
def project_create_view(request):
    tenant = request.tenant
    if not tenant:
        messages.warning(request, 'You need to be part of an organization first.')
        return redirect('register_org')
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.tenant = tenant
            project.created_by = request.user
            project.save()
            messages.success(request, f'Project "{project.name}" created!')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'tasks/project_form.html', {'form': form, 'action': 'Create'})


@login_required
def project_detail_view(request, pk):
    tenant = request.tenant
    project = get_object_or_404(Project, pk=pk, tenant=tenant)
    tasks = Task.objects.filter(project=project)
    return render(request, 'tasks/project_detail.html', {'project': project, 'tasks': tasks})


@login_required
def task_create_view(request):
    tenant = request.tenant
    if not tenant:
        messages.warning(request, 'You need to be part of an organization first.')
        return redirect('register_org')
    if request.method == 'POST':
        form = TaskForm(request.POST, tenant=tenant)
        if form.is_valid():
            task = form.save(commit=False)
            task.tenant = tenant
            task.created_by = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created!')
            return redirect('project_detail', pk=task.project.pk)
    else:
        form = TaskForm(tenant=tenant)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_update_view(request, pk):
    tenant = request.tenant
    task = get_object_or_404(Task, pk=pk, tenant=tenant)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, tenant=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated!')
            return redirect('project_detail', pk=task.project.pk)
    else:
        form = TaskForm(instance=task, tenant=tenant)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Update', 'task': task})


@login_required
def task_delete_view(request, pk):
    tenant = request.tenant
    task = get_object_or_404(Task, pk=pk, tenant=tenant)
    project_pk = task.project.pk
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
        return redirect('project_detail', pk=project_pk)
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})
