from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/tenants/dashboard/', permanent=False)),
    path('tenants/', include('tenants.urls')),
    path('accounts/', include('accounts.urls')),
    path('tasks/', include('tasks.urls')),
]
