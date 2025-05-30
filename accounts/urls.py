from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('logout/', views.logout, name='logout'),  # 로그아웃 처리 URL
    path('auth/', views.auth_view, name='auth'),
]