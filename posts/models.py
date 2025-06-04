from django.db import models
from django_resized import ResizedImageField
from django.conf import settings

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    image = ResizedImageField(
        size=[400, 400],
        crop=['middle', 'center'],
        upload_to='posts/images/',
        quality=90,
        blank=True,
        null=True,
        verbose_name='Post Image'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        
    )
    
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='like_posts',
        blank=True
    )

class Comment(models.Model):
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    image = ResizedImageField(
        size=[300, 300],
        crop=['middle', 'center'],
        upload_to='comments/images/',
        quality=90,
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