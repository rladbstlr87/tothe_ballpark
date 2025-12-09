from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode


class PolicyConsentRequiredMiddleware:
    """
    Redirect authenticated users to reconsent when their terms/privacy versions are stale.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._allowed_paths_cache = None

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def _get_allowed_paths(self):
        """
        Build a path-based allowlist so it works even before resolver_match is populated.
        """
        if self._allowed_paths_cache is not None:
            return self._allowed_paths_cache

        try:
            allowed = {
                reverse('accounts:terms'),
                reverse('accounts:privacy'),
                reverse('accounts:reconsent'),
                reverse('accounts:logout'),
                reverse('accounts:auth'),
            }
        except Exception:
            # Fallback to static paths if reverse is not available yet.
            allowed = {
                '/accounts/terms/',
                '/accounts/privacy/',
                '/accounts/reconsent/',
                '/accounts/logout/',
                '/accounts/auth/',
            }

        self._allowed_paths_cache = allowed
        return allowed

    def process_request(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None

        needs_reconsent = (
            user.terms_version != getattr(settings, 'TERMS_VERSION', None) or
            user.privacy_version != getattr(settings, 'PRIVACY_VERSION', None)
        )
        if not needs_reconsent:
            return None

        path = request.path

        # Allow static/media.
        if path.startswith('/static/') or path.startswith('/media/'):
            return None

        # Allow policy/reconsent/auth pages.
        if path in self._get_allowed_paths():
            return None

        # Redirect to reconsent with next.
        reconsent_url = reverse('accounts:reconsent')
        params = {'next': request.get_full_path()}
        return redirect(f"{reconsent_url}?{urlencode(params)}")
