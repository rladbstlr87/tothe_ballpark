from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User
from cal import views

# 로그아웃 뷰 - 로그인된 사용자만 로그아웃 가능
@login_required
def logout(request):
    auth_logout(request)  # 세션에서 사용자 로그아웃
    return redirect('/')  # 로그아웃 후 홈으로 이동

# 메인 페이지 접근 시 리다이렉트
def home(request):
    return redirect('/')

# 🔁 회원가입/로그인 통합 처리 뷰
def auth_view(request):
    # 쿼리스트링에서 ?mode=login 또는 ?mode=signup 받아오기 (기본값은 'login')
    mode = request.GET.get('mode', 'login')

    # POST 요청 처리: 사용자가 로그인/회원가입 폼 제출 시
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'signup':
            mode = 'signup'
            signup_form = CustomUserCreationForm(request.POST)
            login_form = CustomAuthenticationForm()
            if signup_form.is_valid():
                user = signup_form.save()  # 사용자 생성
                auth_login(request, user)  # 자동 로그인 처리
                return redirect('cal:calendar')  # 캘린더로 이동

        elif action == 'login':
            mode = 'login'
            login_form = CustomAuthenticationForm(request, data=request.POST)
            signup_form = CustomUserCreationForm()
            if login_form.is_valid():
                auth_login(request, login_form.get_user())  # 로그인
                return redirect('cal:calendar')  # 캘린더로 이동

        else:
            # POST인데 action이 login/signup이 아닐 경우
            signup_form = CustomUserCreationForm()
            login_form = CustomAuthenticationForm()

    else:
        # GET 요청인 경우: 빈 폼 준비
        signup_form = CustomUserCreationForm()
        login_form = CustomAuthenticationForm()

    # auth.html 렌더링 - 폼들과 모드 전달
    return render(request, 'auth.html', {
        'signup_form': signup_form,
        'login_form': login_form,
        'mode': mode,
    })