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
    mode = request.GET.get('mode', 'login')

    if request.method == 'POST':
        if mode == 'signup':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                auth_login(request, user)
                return redirect('cal:calendar')
        else:  # mode == 'login'
            form = CustomAuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                auth_login(request, user)
                return redirect('cal:calendar')
    else:
        form = CustomUserCreationForm() if mode == 'signup' else CustomAuthenticationForm()

    context = {
        'mode': mode,
        'signup_form': CustomUserCreationForm(),
        'login_form': CustomAuthenticationForm(request),
    }
    return render(request, 'auth.html', context)