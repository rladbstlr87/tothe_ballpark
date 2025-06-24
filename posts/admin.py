from django.contrib import admin
from .models import Post
# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'created_at', 'KBO_TEAMS', 'updated_at', 'user',  'category')
    search_fields = ('title', 'content')
    list_filter = ('created_at',)
