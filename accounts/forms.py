from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User
import os

# 사용자 정의 회원가입 폼
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'email', 'team', 'profile_image', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': '아이디',
                'autocomplete': 'off',
            }),
            'nickname': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': '닉네임',
                'autocomplete': 'off',
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': '이메일',
                'autocomplete': 'off',
            }),
            'team': forms.Select(attrs={
                'class': 'form-field',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-field')

        self.fields['team'].empty_label = '팀 선정'

    def clean_team(self):
        team = self.cleaned_data.get('team')
        if not team:
            raise forms.ValidationError('팀을 선택해주세요.')
        return team

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


# 사용자 정의 로그인 폼
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        # 아이디 입력 필드 커스터마이징
        self.fields['username'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '아이디'
        })

        # 비밀번호 입력 필드 커스터마이징
        self.fields['password'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '비밀번호'
        })


class PasswordChangeCustomForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '현재 비밀번호',
            'class': 'w-full mb-2 px-3 py-2 rounded border',
            'style': 'border-color: #dce9f9;',
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '새 비밀번호',
            'class': 'w-full mb-2 px-3 py-2 rounded border',
            'style': 'border-color: #dce9f9;',
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '새 비밀번호 확인',
            'class': 'w-full mb-2 px-3 py-2 rounded border',
            'style': 'border-color: #dce9f9;',
        })
    )

class NicknameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname']
        widgets = {
            'nickname': forms.TextInput(attrs={
                'placeholder': '새 닉네임',
                'class': 'w-full mb-2 px-3 py-2 rounded border',
                'style': 'border-color: #dce9f9;',
            })
        }

class TeamChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['team']
        widgets = {
            'team': forms.Select(attrs={
                'class': 'w-full mb-2 px-3 py-2 rounded border',
                'style': 'border-color: #dce9f9;',
            })
        }

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']

    def save(self, commit=True):
        # 프로필 이미지를 변경할 때, 기존 이미지를 삭제하는 로직
        instance = super().save(commit=False)
        
        # 기존 이미지가 있다면 삭제
        if instance.pk:  # 기존 인스턴스가 있다면
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.profile_image and old_instance.profile_image != instance.profile_image:
                # 기존 이미지를 삭제
                if os.path.isfile(old_instance.profile_image.path):
                    os.remove(old_instance.profile_image.path)

        if commit:
            instance.save()

        return instance