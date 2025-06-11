from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# ✅ 사용자 정의 회원가입 폼
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # 커스텀 사용자 모델 사용
        fields = ('username', 'nickname', 'email', 'team', 'password1', 'password2')  # 사용자 입력 필드
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': '아이디',
                'autocomplete': 'off'
            }),
            'nickname': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': '닉네임',
                'autocomplete': 'off'
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-field',
                'placeholder': '이메일',
                'autocomplete': 'off'
            }),
            'team': forms.Select(attrs={
                'class': 'form-field'
            })
        }

    # ✅ 초기화 시 패스워드 필드에 스타일, placeholder 추가
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-3 py-2 mb-4 rounded-md ',
                'style': 'border: 1px solid #d9d2b4; border-radius: 6px;',
            })

        # 팀 선택 필드에 '팀 선정'이라는 기본 옵션 추가
        self.fields['team'].empty_label = '팀 선정'

    # ✅ 팀 선택 안 했을 때 검증 에러 발생
    def clean_team(self):
        team = self.cleaned_data.get('team')
        if not team:
            raise forms.ValidationError('팀을 선택해주세요.')
        return team

    # ✅ 이메일을 명시적으로 저장
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


# ✅ 사용자 정의 로그인 폼
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
