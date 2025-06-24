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
            'image': forms.ClearableFileInput(attrs={
                'class': 'mt-2 text-sm text-gray-700'
                'block w-full text-sm text-gray-700 '
                'file:mr-4 file:py-2 file:px-4 '
                'file:rounded-md file:border-0 '
                'file:bg-gray-100 file:text-gray-800 '
                'hover:file:bg-gray-200'
            }),
        }