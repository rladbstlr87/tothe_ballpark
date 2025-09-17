from django.db import models
from django.conf import settings
import os

def get_upload_path(instance, filename):
    return os.path.join(
      f'posts/images/{instance.post.id}', f'{filename}.webp')

def get_comment_upload_path(instance, filename):
    return os.path.join(
      f'comments/images/{instance.post.id}', f'{filename}.webp')

class Post(models.Model):
    KBO_TEAMS = [
        ('HH', '한화'),
        ('WO', '키움'),
        ('HT', 'KIA'),
        ('LG', 'LG'),
        ('OB', '두산'),
        ('SS', '삼성'),
        ('LT', '롯데'),
        ('NC', 'NC'),
        ('KT', 'KT'),
        ('SSG', 'SSG'),
        ('ETC', '일반'),
    ]
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        
    )
    
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='like_posts',
        blank=True
    )

    category = models.CharField(
        max_length=10,
        choices=KBO_TEAMS,
        default='ETC',
        verbose_name='카테고리'
    )

class Comment(models.Model):
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    image = models.ImageField(
        upload_to=get_comment_upload_path,
        blank=True,
        null=True,
        verbose_name='Comment Image'
    )
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='like_comments',
        blank=True
    )

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_upload_path)
