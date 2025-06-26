from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'posts'

urlpatterns = [
    path('', views.post_index, name='post_index'),
    path('create/', views.create, name='create'),
    path('<int:id>', views.detail, name='detail'),
    path('<int:id>/delete/', views.delete, name='delete'),
    path('<int:id>/update/', views.update, name='update'),
    
    path('<int:post_id>/comments/create/', views.comment_create, name='comment_create'),
    path('<int:post_id>/comments/<int:comment_id>/update/', views.comment_update, name='comment_update'),
    path('<int:post_id>/comments/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:post_id>/like', views.post_like, name='post_like'),
    path('<int:id>/like-async/', views.like_async, name='like_async'),
    path('comments/<int:comment_id>/like-async/', views.comment_like_async, name='comment_like_async'),
    
]


