# Month 6: SaaS Platform — Multi-Tenant Project Management

A production-oriented **Software-as-a-Service** project management application built with **Django**.  
Organisations (tenants) can be created and managed independently, with full isolation between them.

---

## Features

| Feature | Details |
|---|---|
| **Multi-tenancy** | Tenant isolation enforced via middleware and per-query filtering |
| **Organisation plans** | Free / Pro / Enterprise with configurable user & project limits |
| **User roles** | Owner · Admin · Member per organisation |
| **Projects** | Create and browse projects scoped to your tenant |
| **Tasks** | Full CRUD — title, description, status, priority, assignee |
| **Authentication** | Register, login, logout with Django auth |
| **Admin panel** | Full Django admin for all models |
| **Tests** | 26 passing unit + integration tests |

---

## Project Structure

```
m6/
├── saas_platform/         Django project settings & root URLs
├── accounts/              User registration, login, UserProfile model
├── tenants/               Tenant (organisation) model & middleware
├── tasks/                 Projects & Tasks CRUD
├── templates/             Bootstrap 5 HTML templates
├── static/css/style.css   Custom CSS
├── tests/                 26 passing tests
├── pytest.ini
├── requirements.txt
└── manage.py
```

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply database migrations
python manage.py migrate

# 3. (Optional) Create a superuser for admin access
python manage.py createsuperuser

# 4. Run the development server
python manage.py runserver

# 5. Open http://127.0.0.1:8000/
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All **26 tests** pass, covering models, views, auth, dashboard, and multi-tenant isolation.

---

## Architecture Highlights

- **TenantMiddleware** attaches `request.tenant` from the logged-in user's profile.
- All queries are automatically scoped: `Model.objects.filter(tenant=request.tenant)`.
- Tenant isolation verified by test: a user from Org A cannot access Org B's tasks.
- Role model: Owner → Admin → Member per organisation.
