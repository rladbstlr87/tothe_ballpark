from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'accounts'

urlpatterns = [
    path('logout/', views.logout, name='logout'),
    path('auth/', views.auth_view, name='auth'),
    path('find_id/', views.find_id_view, name='find_id'),
    path('reset_password/', views.reset_password_view, name='reset_password'),
    path('confirm_verification_code/', views.confirm_verification_code, name='confirm_verification_code'),
    path('set_new_password/', views.set_new_password, name='set_new_password'),
    path('check-duplicate/', views.check_duplicate, name='check_duplicate'),
    path('mypage/', views.mypage, name='mypage'),
    path('update_profile_image/', views.update_profile_image, name='update_profile_image'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)