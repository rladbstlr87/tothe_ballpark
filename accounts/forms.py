from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

def clean_team(self):
    team = self.cleaned_data.get('team')
    if not team:
        raise forms.ValidationError('팀을 선택해주세요.')
    return team

# 사용자 정의 회원가입 폼
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'team', 'password1', 'password2')

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': '아이디'
            }),
            'nickname': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': '닉네임'
            }),
            'team': forms.Select(attrs={
                'class': 'form-field',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '비밀번호'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '비밀번호 확인'
        })
        self.fields['team'].empty_label = '팀 선정'

    # ✅ team 유효성 검사
    def clean_team(self):
        team = self.cleaned_data.get('team')
        if not team:
            raise forms.ValidationError('팀을 선택해주세요.')
        return team


# 사용자 정의 로그인 폼
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '아이디'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '비밀번호'
        })
