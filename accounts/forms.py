from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User
from django.conf import settings
from django.utils import timezone
import os

# 회원가입 폼
class CustomUserCreationForm(UserCreationForm):
    terms_agree = forms.BooleanField(
        required=True,
        label='이용약관 동의',
        error_messages={'required': '서비스 이용약관에 동의해주세요.'}
    )
    privacy_agree = forms.BooleanField(
        required=True,
        label='개인정보 처리방침 동의',
        error_messages={'required': '개인정보 처리방침에 동의해주세요.'}
    )

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
        user.terms_version = getattr(settings, 'TERMS_VERSION', None)
        user.privacy_version = getattr(settings, 'PRIVACY_VERSION', None)
        now = timezone.now()
        user.terms_agreed_at = now
        user.privacy_agreed_at = now
        if commit:
            user.save()
        return user


# 로그인 폼
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

# 변경 폼들
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
        instance = super().save(commit=False)
        if instance.pk:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.profile_image and old_instance.profile_image != instance.profile_image:
                if os.path.isfile(old_instance.profile_image.path):
                    os.remove(old_instance.profile_image.path)

        if commit:
            instance.save()
        return instance


class ReconsentForm(forms.Form):
    terms_agree = forms.BooleanField(
        required=True,
        label='이용약관에 동의합니다.',
        error_messages={'required': '두 항목 모두 동의하지 않으면 서비스 이용이 어렵습니다.'}
    )
    privacy_agree = forms.BooleanField(
        required=True,
        label='개인정보 처리방침에 동의합니다.',
        error_messages={'required': '두 항목 모두 동의하지 않으면 서비스 이용이 어렵습니다.'}
    )

    def save(self, user):
        user.terms_version = getattr(settings, 'TERMS_VERSION', None)
        user.privacy_version = getattr(settings, 'PRIVACY_VERSION', None)
        now = timezone.now()
        user.terms_agreed_at = now
        user.privacy_agreed_at = now
        user.save()
        return user
