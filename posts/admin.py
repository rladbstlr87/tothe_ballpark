from django.contrib import admin
from .models import Post
# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'created_at', 'KBO_TEAMS', 'updated_at', 'user',  'category')  # 관리자 페이지에 보일 필드 지정
    search_fields = ('title', 'content')              # 검색 가능 필드
    list_filter = ('created_at',)                     # 필터 사이드바
