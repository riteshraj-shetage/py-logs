"""
Tests for the SaaS Platform (m6).

Covers: tenant model, user profiles, project & task CRUD,
tenant middleware, and dashboard/view access control.
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from tenants.models import Tenant
from accounts.models import UserProfile
from tasks.models import Project, Task


def make_user(username='alice', password='testpass123'):
    return User.objects.create_user(username=username, password=password, email=f'{username}@example.com')


def make_tenant(owner, name='Acme Corp', plan='free'):
    return Tenant.objects.create(name=name, slug=name.lower().replace(' ', '-'), owner=owner, plan=plan)


def make_profile(user, tenant, role='member'):
    return UserProfile.objects.create(user=user, tenant=tenant, role=role)


def make_project(tenant, user, name='Alpha'):
    return Project.objects.create(tenant=tenant, name=name, created_by=user)


def make_task(tenant, project, user, title='Task 1', status='todo', priority='medium'):
    return Task.objects.create(
        tenant=tenant, project=project, title=title,
        status=status, priority=priority, created_by=user
    )


# ──────────────────────────────────────────────
# Model tests
# ──────────────────────────────────────────────

class TenantModelTest(TestCase):
    def setUp(self):
        self.owner = make_user('owner')

    def test_tenant_str(self):
        tenant = make_tenant(self.owner)
        self.assertEqual(str(tenant), 'Acme Corp')

    def test_tenant_defaults(self):
        tenant = make_tenant(self.owner)
        self.assertEqual(tenant.plan, 'free')
        self.assertTrue(tenant.is_active)
        self.assertEqual(tenant.max_users, 5)
        self.assertEqual(tenant.max_projects, 3)

    def test_tenant_ordering(self):
        make_tenant(self.owner, 'Zebra Ltd')
        make_tenant(self.owner, 'Alpha Corp')
        names = list(Tenant.objects.values_list('name', flat=True))
        self.assertEqual(names, sorted(names))


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.tenant = make_tenant(self.user)

    def test_profile_str(self):
        profile = make_profile(self.user, self.tenant, role='owner')
        self.assertIn(self.user.username, str(profile))

    def test_profile_default_role(self):
        profile = UserProfile.objects.create(user=self.user, tenant=self.tenant)
        self.assertEqual(profile.role, 'member')


class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.tenant = make_tenant(self.user)

    def test_project_str(self):
        project = make_project(self.tenant, self.user)
        self.assertEqual(str(project), 'Alpha')

    def test_project_tenant_relation(self):
        make_project(self.tenant, self.user)
        self.assertEqual(self.tenant.projects.count(), 1)


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.tenant = make_tenant(self.user)
        self.project = make_project(self.tenant, self.user)

    def test_task_str(self):
        task = make_task(self.tenant, self.project, self.user)
        self.assertEqual(str(task), 'Task 1')

    def test_task_status_default(self):
        task = make_task(self.tenant, self.project, self.user)
        self.assertEqual(task.status, 'todo')

    def test_task_tenant_relation(self):
        make_task(self.tenant, self.project, self.user)
        self.assertEqual(self.tenant.tasks.count(), 1)

    def test_task_project_relation(self):
        make_task(self.tenant, self.project, self.user, title='T1')
        make_task(self.tenant, self.project, self.user, title='T2')
        self.assertEqual(self.project.tasks.count(), 2)


# ──────────────────────────────────────────────
# View / access-control tests
# ──────────────────────────────────────────────

class AuthViewTest(TestCase):
    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'Complex!Pass99',
            'password2': 'Complex!Pass99',
        })
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)

    def test_login_redirects_authenticated(self):
        user = make_user('bob')
        self.client.force_login(user)
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('tenant_dashboard'))


class DashboardViewTest(TestCase):
    def setUp(self):
        self.owner = make_user('dashowner')
        self.tenant = make_tenant(self.owner, 'Dash Corp')
        self.profile = make_profile(self.owner, self.tenant, role='owner')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('tenant_dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('tenant_dashboard')}")

    def test_dashboard_shows_tenant(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('tenant_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dash Corp')

    def test_dashboard_no_tenant(self):
        user = make_user('lonely')
        self.client.force_login(user)
        response = self.client.get(reverse('tenant_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Organization Yet')


class ProjectViewTest(TestCase):
    def setUp(self):
        self.owner = make_user('projowner')
        self.tenant = make_tenant(self.owner, 'Proj Corp')
        self.profile = make_profile(self.owner, self.tenant, role='owner')

    def test_project_list_requires_login(self):
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 302)

    def test_project_create(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('project_create'), {
            'name': 'Beta Project',
            'description': 'A new project',
        })
        self.assertEqual(Project.objects.filter(name='Beta Project', tenant=self.tenant).count(), 1)

    def test_project_detail(self):
        project = make_project(self.tenant, self.owner, 'Gamma')
        self.client.force_login(self.owner)
        response = self.client.get(reverse('project_detail', args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gamma')


class TaskViewTest(TestCase):
    def setUp(self):
        self.owner = make_user('taskowner')
        self.tenant = make_tenant(self.owner, 'Task Corp')
        self.profile = make_profile(self.owner, self.tenant, role='owner')
        self.project = make_project(self.tenant, self.owner, 'My Project')

    def test_task_create(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('task_create'), {
            'title': 'Fix bug',
            'description': '',
            'project': self.project.pk,
            'status': 'todo',
            'priority': 'high',
            'assignee': '',
        })
        self.assertEqual(Task.objects.filter(title='Fix bug', tenant=self.tenant).count(), 1)

    def test_task_update(self):
        task = make_task(self.tenant, self.project, self.owner, title='Old Title')
        self.client.force_login(self.owner)
        response = self.client.post(reverse('task_update', args=[task.pk]), {
            'title': 'New Title',
            'description': '',
            'project': self.project.pk,
            'status': 'done',
            'priority': 'low',
            'assignee': '',
        })
        task.refresh_from_db()
        self.assertEqual(task.title, 'New Title')
        self.assertEqual(task.status, 'done')

    def test_task_delete(self):
        task = make_task(self.tenant, self.project, self.owner, title='To Delete')
        self.client.force_login(self.owner)
        response = self.client.post(reverse('task_delete', args=[task.pk]))
        self.assertEqual(Task.objects.filter(pk=task.pk).count(), 0)

    def test_task_isolation(self):
        """Tasks from another tenant must not be accessible."""
        other_user = make_user('other')
        other_tenant = make_tenant(other_user, 'Other Corp')
        make_profile(other_user, other_tenant, role='owner')
        other_project = make_project(other_tenant, other_user, 'Other Project')
        other_task = make_task(other_tenant, other_project, other_user, title='Private Task')

        self.client.force_login(self.owner)
        response = self.client.get(reverse('task_update', args=[other_task.pk]))
        self.assertEqual(response.status_code, 404)


class RegisterOrgViewTest(TestCase):
    def test_register_org_creates_tenant_and_profile(self):
        user = make_user('orgcreator')
        self.client.force_login(user)
        response = self.client.post(reverse('register_org'), {
            'name': 'New Venture',
            'plan': 'pro',
        })
        self.assertEqual(Tenant.objects.filter(name='New Venture').count(), 1)
        tenant = Tenant.objects.get(name='New Venture')
        self.assertEqual(tenant.slug, 'new-venture')
        self.assertEqual(UserProfile.objects.filter(user=user, tenant=tenant, role='owner').count(), 1)
