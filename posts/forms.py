from django.forms import ModelForm
from .models import Post, Comment
from django import forms
    
class PostForm(ModelForm):
    class Meta():
        model = Post
        fields = ('title', 'content','category')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-400'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-md '
                        'focus:outline-none focus:ring-2 focus:ring-sky-400 '
                        'placeholder-gray-400 text-base resize-y'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-400 bg-white'
            })
        }

class CommentForm(ModelForm):        
    class Meta():
        model = Comment
        fields = ('content', 'image' )
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full border border-gray-300 p-3 rounded resize-none '
                        'focus:outline-none focus:ring-2 focus:ring-sky-200'
            }),
        }