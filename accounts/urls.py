from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),  # 회원가입 페이지 URL
    path('login/', views.login, name='login'),  # 로그인 페이지 URL
    path('logout/', views.logout, name='logout'),  # 로그아웃 처리 URL
    path('auth/', views.auth_view, name='auth'),
]