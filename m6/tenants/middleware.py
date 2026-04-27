from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """Sets request.tenant based on the authenticated user's profile."""

    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.profile
                request.tenant = profile.tenant
            except Exception:
                request.tenant = None
        else:
            request.tenant = None
