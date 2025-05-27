from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from django import forms # django에서 폼을 만들고 다루기 위한 모듈

class CustomUserCreationForm(UserCreationForm): # usercreationform을 상속받아서 내 사용자 모델(user)에 맞게 확장한 회원가입 폼 생성성
    class Meta():
        model = User
        fields = ('username', 'nickname', 'team', 'password1', 'password2') # user 모델을 기반으로 하는 폼 원래는 password1 (비밀번호 입력) password2(비밀번호 확인)은 필요없었지만 하나씩 디자인하기 위해서 추가 
        # 각 필드에 들어갈 HTML input 태그 속성을 커스터 마이징 할 수 있는 곳곳
        widgets = {
                'username': forms.TextInput(attrs={ # attrs로 HTML 속성 지정정
                    'class': 'w-full px-4 py-2 border rounded-lg',
                    # class는 tailwindcss 클래스를 지정해서 스타일링
                    # w-full : 너비 px-4 py-2: 좌우 1단위 패딩 4, 상하 2
                    # border : 테두리 표시
                    # rounded-lg :둥근 모서리 적용 
                    'placeholder': 'Username'
                    # 입력란에 희미하게 뜨는 안내 문구로 'username'을 표시 
                }),
                # team 필드는 select 박스로 렌더링
                # tailwind  스타일 적용해서 너비 100%, 패딩, 테두리, 둥근 모서리 
                'team': forms.Select(attrs={
                    'class': 'w-full px-4 py-2 border rounded-lg',
                }),
                'nickname': forms.TextInput(attrs={'placeholder': 'Nickname'})
                
        }
    # usercreationform이 기본적으로 password1과 password2 필드에 widget을 지정해도 무시하는 경우 발생
    # __init__() 메서드에서 수동으로 위젯 속성을 다시 덮어쓰기          
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Confirm Password'
        })
            
        
# 로그인 폼을 커스터마이징 하기 위해서 
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs): # 생성자 함수로 폼이 생성될 때 실행 
        # request=None은 로그인 폼에서 사용자 인증 등에 필요함
        #         *args, **kwargs는 추가 인자를 받음
        # 부모 클래스(기본 로그인 폼) 초기화 메서드를 호출해서 원래 기능 유지 
        super(CustomAuthenticationForm, self).__init__(request, *args, **kwargs)
        
        # username 필드의 위젯(입력란)에 tailwind css 클래스를 붙이고 placeholder를 지정
        # update()는 기본 속성을 유지하면서 덮어쓰기 위해서 
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Password'
        })
        self.fields['nickname'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-lg',
            'placeholder': 'Nickname'
        })

# input 요소에 tailwind 스타일을 적용하기 위해, forms.py에서 각 필드의 widget을 커스터마이징 해주기
