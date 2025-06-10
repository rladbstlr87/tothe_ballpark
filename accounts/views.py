from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User
from cal import views
import json
import string
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

@csrf_exempt
def find_id_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")

        # 해당 이메일로 등록된 모든 사용자 찾기
        users = User.objects.filter(email=email)

        if users.exists():
            usernames = [user.username for user in users]
            username_list = "\n".join(usernames)

            send_mail(
                subject="아이디 찾기 결과입니다",
                message=f"해당 이메일로 등록된 아이디 목록입니다:\n\n{username_list}",
                from_email=None,  # EMAIL_HOST_USER 설정되어 있으면 None 가능
                recipient_list=[email],
            )
            return JsonResponse({"success": True, "message": "아이디 목록이 이메일로 전송되었습니다."})
        else:
            return JsonResponse({"success": False, "message": "해당 이메일로 등록된 계정을 찾을 수 없습니다."})

# 임시 저장소
VERIFICATION_CODES = {}
VERIFIED_USERS = set()

def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


@csrf_exempt
def reset_password_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        username = data.get("username")

        try:
            user = User.objects.get(username=username, email=email)
            code = generate_code(6)
            VERIFICATION_CODES[username] = code

            send_mail(
                subject="비밀번호 재설정 인증번호",
                message=f"비밀번호 재설정을 위한 인증번호는 {code} 입니다.",
                from_email=None,
                recipient_list=[email],
            )

            return JsonResponse({"success": True, "message": "인증번호가 이메일로 전송되었습니다."})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "아이디 또는 이메일이 올바르지 않습니다."})


@csrf_exempt
def confirm_verification_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        code = data.get("code")

        saved_code = VERIFICATION_CODES.get(username)
        if saved_code == code:
            VERIFIED_USERS.add(username)
            return JsonResponse({"success": True, "message": "인증에 성공했습니다."})
        else:
            return JsonResponse({"success": False, "message": "인증번호가 일치하지 않습니다."})


@csrf_exempt
def set_new_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        new_password = data.get("new_password")

        if username not in VERIFIED_USERS:
            return JsonResponse({"success": False, "message": "인증되지 않은 사용자입니다."})

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            VERIFIED_USERS.discard(username)
            VERIFICATION_CODES.pop(username, None)
            return JsonResponse({"success": True, "message": "비밀번호가 성공적으로 변경되었습니다."})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "사용자를 찾을 수 없습니다."})
        
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