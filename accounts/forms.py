from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# 사용자 정의 회원가입 폼
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'team', 'password1', 'password2')  # 입력 받을 필드

        # HTML input 요소에 TailwindCSS 스타일 적용
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Username'
            }),
            'nickname': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg',
                'placeholder': 'Nickname'
            }),
            'team': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 기본 password 필드들의 위젯 스타일 수동 커스터마이징
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Confirm Password'
        })

# 사용자 정의 로그인 폼
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(request, *args, **kwargs)

        # username과 password 필드에 TailwindCSS 스타일 적용
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Password'
        })