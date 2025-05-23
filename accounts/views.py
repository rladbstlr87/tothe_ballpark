from django.shortcuts import render

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
            return redirect('accounts:login')  # 저장 후 게시물 목록 페이지로 리다이렉트
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

# 회원가입과 로그인 전환 뷰 
def auth_view(request):
    mode = request.GET.get('mode', 'login')  
    # url 쿼리스트링에서 mode라는 값을 읽어옴(?mode=signup) 
    # 만약 없으면 기본값으로 login을 설정
    # 화면에서 로그인 폼을 먼저 보여줄지, 회원가입 폼을 먼저 보여줄지 결정 

    if request.method == 'POST': # 폼 제출을 했는지 여부( post면 사용자가 로그인 또는 회원가입 폼을 제출했다는 의미미)
        if request.POST.get('action') == 'signup': # 회원가입 일 경우우
            mode = 'signup'  # 화면에서 회원가입 폼을 보여주도록 mode값을 'signup'으로 지정정
            signup_form = CustomUserCreationForm(request.POST) # 회원가입 폼 데이터로 인스턴스 생성성
            login_form = CustomAuthenticationForm() # 로그인 폼은 비워진 상태로 준비(회원가입 폼만 처리 중중)
            if signup_form.is_valid(): # 회원가입 폼이 유효한지 검사 
                user = signup_form.save() # 폼에 입력된 내용을 바탕으로 실제 회원 데이터 저장장
                auth_login(request, user)
                return redirect('cal:calendar') # 회원가입하고 바로 캘린더로 이동
        elif request.POST.get('action') == 'login': #로그인시 
            mode = 'login'
            login_form = CustomAuthenticationForm(request, data=request.POST)
            signup_form = CustomUserCreationForm()
            if login_form.is_valid():
                auth_login(request, login_form.get_user()) # 로그인 성공 시 세션에 사용자 정보를 저장해 로그인 처리리
                return redirect('cal:calendar') # 로그인 성공시 캘린더로 이동동
        else: # 비정상 post일 경우(action이 signup도 아니고 login도 아닐경우)
            signup_form = CustomUserCreationForm() # 로그인과 회원가입 폼 모두 빈 상태로 초기화 
            login_form = CustomAuthenticationForm()
    else: # 요청이 post가 아니면 (즉 get요청, 페이지 최초 접속 시)
        signup_form = CustomUserCreationForm()
        login_form = CustomAuthenticationForm()

    return render(request, 'auth.html', {       # 최종적으로 auth.html 템플릿에 준비한 폼들과 mode 변수를 넘겨서 렌더링링
        'signup_form': signup_form,
        'login_form': login_form,
        'mode': mode, # mode에 따라 로그인 폼 또는 회원가입 폼 중 어떤 걸 기본으로 보여줄지 결정 
    })