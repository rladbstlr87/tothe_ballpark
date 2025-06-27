from django.contrib import admin
from django.urls import path, include
from cal import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),  # 기본 URL을 cal 앱의 index 뷰로 설정
    path('admin/', admin.site.urls),
    path('cal/', include('cal.urls')),
    path('accounts/', include('accounts.urls')),  # accounts 앱의 URL 포함
    path('posts/', include('posts.urls')), 
    path('jikdoltest/', include('jikdoltest.urls')),  # jikdoltest 앱의 URL 포함
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)