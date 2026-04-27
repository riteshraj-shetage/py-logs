from django import forms
from .models import Project, Task


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'project', 'status', 'priority', 'assignee']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields['project'].queryset = Project.objects.filter(tenant=tenant)
            from django.contrib.auth.models import User
            member_ids = tenant.members.values_list('user_id', flat=True)
            self.fields['assignee'].queryset = User.objects.filter(id__in=member_ids)
