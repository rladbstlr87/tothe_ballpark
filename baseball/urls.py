from django.contrib import admin
from django.urls import path, include
from cal import views
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('', views.index, name='index'),  # 기본 URL을 cal 앱의 index 뷰로 설정
    path('admin/', admin.site.urls),
    path('cal/', include('cal.urls')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts_web')),
    path('posts/', include('posts.urls')), 
    path('jikdoltest/', include('jikdoltest.urls')),
    
    path('api/', include(('accounts.api_urls', 'accounts'), namespace='accounts_api')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs', SpectacularSwaggerView.as_view(url_name='schema')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)