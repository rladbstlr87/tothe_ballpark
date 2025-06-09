from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# 사용자 정의 회원가입 폼
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'team', 'password1', 'password2')

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': 'Username'
            }),
            'nickname': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': 'Nickname'
            }),
            'team': forms.Select(attrs={
                'class': 'form-field'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': 'Confirm Password'
        })

# 사용자 정의 로그인 폼
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': 'Password'
        })
