from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect  # 템플릿 렌더링 및 리다이렉트를 위한 함수
from .forms import CustomUserCreationForm, CustomAuthenticationForm  # 커스텀 회원가입 및 로그인 폼
from django.contrib.auth import login as auth_login  # 사용자 로그인 처리 함수
from django.contrib.auth import logout as auth_logout  # 사용자 로그아웃 처리 함수
from .models import User  # User 모델 가져오기
from django.contrib.auth.decorators import login_required  # 로그인 여부를 확인하는 데코레이터
from cal import views  # cal 앱의 views 모듈 가져오기

# 회원가입 뷰
def signup(request):
    if request.method == 'POST':  # POST 요청일 경우, 폼 데이터를 처리
        form = CustomUserCreationForm(request.POST, request.FILES)  # 폼에 데이터와 파일 전달
        if form.is_valid():  # 폼 유효성 검사
            form.save()  # 유효하면 사용자 저장
            return redirect('cal:calendar')  # 저장 후 게시물 목록 페이지로 리다이렉트
    else:  # GET 요청일 경우, 빈 폼 생성
        form = CustomUserCreationForm()

    context = {
        'form': form,  # 템플릿에 전달할 폼 객체
    }
    return render(request, 'signup.html', context)  # 회원가입 템플릿 렌더링

# 로그인 뷰
def login(request):
    if request.method == 'POST':  # POST 요청일 경우, 폼 데이터를 처리
        form = CustomAuthenticationForm(request, request.POST)  # 폼에 요청 객체와 데이터 전달
        if form.is_valid():  # 폼 유효성 검사
            user = form.get_user()  # 유효하면 사용자 객체 가져오기
            auth_login(request, user)  # 사용자 로그인 처리
            return redirect('cal:calendar')  # 로그인 후 게시물 목록 페이지로 리다이렉트
    else:  # GET 요청일 경우, 빈 폼 생성
        form = CustomAuthenticationForm()
    context = {
        'form': form,  # 템플릿에 전달할 폼 객체
    }
    return render(request, 'login.html', context)  # 로그인 템플릿 렌더링

# 로그아웃 뷰
@login_required  # 로그인된 사용자만 접근 가능
def logout(request):
    auth_logout(request)  # 사용자 로그아웃 처리
    return redirect('/')  # 로그아웃 후 기본 페이지로 리다이렉트

# 메인 페이지 뷰
def home(request):
    return redirect('/')