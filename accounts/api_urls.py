from django.urls import path
from .api import (
    SignupAPIView,
    DuplicateCheckAPIView,
    FindIdAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    PasswordResetSetAPIView,
)

app_name = "accounts_api"

urlpatterns = [
    path("signup/", SignupAPIView.as_view(), name="signup"),
    path("check-duplicate/", DuplicateCheckAPIView.as_view(), name="check_duplicate"),
    path("find-id/", FindIdAPIView.as_view(), name="find_id"),
    path("password/reset/request/", PasswordResetRequestAPIView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmAPIView.as_view(), name="password_reset_confirm"),
    path("password/reset/set/", PasswordResetSetAPIView.as_view(), name="password_reset_set"),
]
