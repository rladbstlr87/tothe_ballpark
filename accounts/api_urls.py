from django.urls import path
from . import api

app_name = 'accounts'

urlpatterns = [
    path('auth/signup/', api.signup, name='signup_api'),
    path('auth/login/', api.login, name='login_api'),
    path('auth/logout/', api.logout, name='logout_api'),
    path('auth/csrf/', api.csrf_issue, name='csrf_api'),
]