from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode


class PolicyConsentRequiredMiddleware:
    """
    로그인한 사용자가 최신 약관/개인정보 버전에 동의하지 않은 경우
    재동의 페이지로 리디렉션합니다.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_names = {
            'accounts:terms',
            'accounts:privacy',
            'accounts:reconsent',
            'accounts:logout',
            'accounts:auth',
        }

    def __call__(self, request):
        response = self.process_request(request)
        if response:
            return response
        return self.get_response(request)

    def process_request(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None

        # 최신 버전 동의 여부 확인
        needs_reconsent = (
            user.terms_version != getattr(settings, 'TERMS_VERSION', None) or
            user.privacy_version != getattr(settings, 'PRIVACY_VERSION', None)
        )
        if not needs_reconsent:
            return None

        path = request.path

        # 정적/미디어, 허용된 URL은 통과
        if path.startswith('/static/') or path.startswith('/media/'):
            return None

        try:
            resolved_name = request.resolver_match.view_name if request.resolver_match else None
        except Exception:
            resolved_name = None

        if resolved_name in self.allowed_names:
            return None

        # 이미 재동의 페이지면 통과
        reconsent_url = reverse('accounts:reconsent')
        if path == reconsent_url:
            return None

        # 재동의 페이지로 리디렉션 (next 포함)
        params = {'next': request.get_full_path()}
        return redirect(f"{reconsent_url}?{urlencode(params)}")
