from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_org_view, name='register_org'),
    path('dashboard/', views.tenant_dashboard_view, name='tenant_dashboard'),
]
