from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Tenant
from .forms import OrganizationRegistrationForm


def register_org_view(request):
    """Register a new organization (tenant). The current user becomes the owner."""
    if request.method == 'POST':
        form = OrganizationRegistrationForm(request.POST)
        if form.is_valid():
            tenant = form.save(commit=False)
            tenant.owner = request.user
            tenant.slug = slugify(tenant.name)
            tenant.save()

            # Create or update the user's profile linking them to this tenant as owner
            from accounts.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.tenant = tenant
            profile.role = 'owner'
            profile.save()

            messages.success(request, f'Organization "{tenant.name}" created successfully!')
            return redirect('tenant_dashboard')
    else:
        form = OrganizationRegistrationForm()

    return render(request, 'tenants/register_org.html', {'form': form})


@login_required
def tenant_dashboard_view(request):
    """Dashboard showing org stats for the current tenant."""
    tenant = request.tenant

    if not tenant:
        messages.info(request, 'You are not part of any organization yet. Create or join one.')
        return render(request, 'tenants/dashboard.html', {'tenant': None})

    member_count = tenant.members.count()
    project_count = tenant.projects.count()
    tasks_qs = tenant.tasks.all()
    total_tasks = tasks_qs.count()
    todo_count = tasks_qs.filter(status='todo').count()
    in_progress_count = tasks_qs.filter(status='in_progress').count()
    done_count = tasks_qs.filter(status='done').count()

    recent_tasks = tasks_qs.order_by('-created_at')[:5]

    context = {
        'tenant': tenant,
        'member_count': member_count,
        'project_count': project_count,
        'total_tasks': total_tasks,
        'todo_count': todo_count,
        'in_progress_count': in_progress_count,
        'done_count': done_count,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'tenants/dashboard.html', context)
