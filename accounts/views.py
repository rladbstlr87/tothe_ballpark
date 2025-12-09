from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from pathlib import Path
from .forms import *
from .models import User
from django.utils import timezone

import json
import string
import random

# 홈 접근 시 달력으로 리디렉션
def home(request):
    return redirect('/')

def auth_view(request):
    mode = request.GET.get('mode', 'login')

    if request.method == 'POST':
        if mode == 'signup':
            signup_form = CustomUserCreationForm(request.POST, request.FILES)
            login_form = CustomAuthenticationForm(request)  # 비워진 로그인 폼
            if signup_form.is_valid():
                user = signup_form.save()
                auth_login(request, user)
                return redirect('cal:calendar')
        else:  # mode == 'login'
            login_form = CustomAuthenticationForm(request, data=request.POST)
            signup_form = CustomUserCreationForm()  # 비워진 회원가입 폼
            if login_form.is_valid():
                user = login_form.get_user()
                auth_login(request, user)
                return redirect('cal:calendar')
    else:
        signup_form = CustomUserCreationForm()
        login_form = CustomAuthenticationForm(request)

    context = {
        'mode': mode,
        'signup_form': signup_form,
        'login_form': login_form,
        'terms_url': getattr(settings, 'TERMS_URL', '#'),
        'privacy_url': getattr(settings, 'PRIVACY_URL', '#'),
    }
    return render(request, 'auth.html', context)

@login_required
def logout(request):
    auth_logout(request)
    return redirect('/')

@csrf_exempt
def find_id_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        users = User.objects.filter(email=email)

        if users.exists():
            usernames = [user.username for user in users]
            username_list = "\n".join(usernames)

            send_mail(
                subject="아이디 찾기 결과입니다",
                message=f"해당 이메일로 등록된 아이디 목록입니다:\n\n{username_list}",
                from_email="직돌이 운영팀 <yerinmin@naver.com>",
                recipient_list=[email],
            )
            return JsonResponse({"success": True, "message": "아이디 목록이 이메일로 전송되었습니다."})
        else:
            return JsonResponse({"success": False, "message": "해당 이메일로 등록된 계정을 찾을 수 없습니다."})

# 인증번호 저장용 변수
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
            # username + email 조합으로 사용자 조회
            # user = User.objects.get(username=username, email=email)
            code = generate_code(6)
            VERIFICATION_CODES[username] = code

            send_mail(
                subject="비밀번호 재설정 인증번호",
                message=f"비밀번호 재설정을 위한 인증번호는 {code} 입니다.",
                from_email="직돌이 운영팀 <seongjin5743@naver.com>",
                recipient_list=[email],
            )
            return JsonResponse({"success": True, "message": "인증번호가 이메일로 전송되었습니다."})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "아이디 또는 이메일이 올바르지 않습니다."})

# 인증번호 확인
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

# 새 비밀번호 설정
@csrf_exempt
def set_new_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        new_password = data.get("new_password")

        # 인증된 사용자만
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

# 아이디,닉네임 중복 확인
@csrf_exempt
def check_duplicate(request):
    if request.method == "POST":
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value")

        if field not in ["username", "nickname"]:
            return JsonResponse({"success": False, "message": "유효하지 않은 필드입니다."})
        exists = User.objects.filter(**{field: value}).exists()

        if exists:
            return JsonResponse({"success": False, "message": f"{field}이(가) 이미 사용 중입니다."})
        else:
            return JsonResponse({"success": True, "message": f"{field}은(는) 사용 가능합니다."})

# 마이페이지
@login_required
def mypage(request):
    user = request.user
    password_form = PasswordChangeCustomForm(user)
    nickname_form = NicknameChangeForm(instance=user)
    team_form = TeamChangeForm(instance=user)
    current_mode = None

    if request.method == 'POST':
        mode = request.POST.get('mode')
        current_mode = mode

        if mode == 'password':
            password_form = PasswordChangeCustomForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
                return redirect('accounts:mypage')
        elif mode == 'nickname':
            nickname_form = NicknameChangeForm(request.POST, instance=user)
            if nickname_form.is_valid():
                nickname_form.save()
                messages.success(request, '닉네임이 성공적으로 변경되었습니다.')
                return redirect('accounts:mypage')
            else:
                messages.error(request, '닉네임이 중복되어 변경에 실패했습니다.')
                user.refresh_from_db()
        elif mode == 'team':
            old_team = user.team
            team_form = TeamChangeForm(request.POST, instance=user)
            if team_form.is_valid():
                team_form.save()
                attended_games = user.attendance_game.all()
                for game in attended_games:
                    if game.team1 == old_team or game.team2 == old_team:
                        game.attendance_users.remove(user)
                messages.success(request, '응원팀이 성공적으로 변경되었습니다.')
                return redirect('accounts:mypage')
            else:
                messages.error(request, '응원팀 변경에 실패했습니다. 입력값을 확인해주세요.')

    context = {
        'password_form': password_form,
        'nickname_form': nickname_form,
        'team_form': team_form,
        'current_mode': current_mode,
    }
    return render(request, 'mypage.html', context)

@login_required
def update_profile_image(request):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        profile_image = request.FILES['profile_image']
        user = request.user
        user.profile_image = profile_image
        user.save()
        messages.success(request, '프로필 이미지가 성공적으로 변경되었습니다.')
        return redirect('accounts:mypage')

    messages.error(request, '프로필 이미지 변경에 실패했습니다.')
    return redirect('accounts:mypage')


def _render_policy(request, title, path_obj, policy_type=None):
    try:
        content = Path(path_obj).read_text(encoding='utf-8')
    except FileNotFoundError:
        content = '문서가 존재하지 않습니다.'
    return render(request, 'policy.html', {'title': title, 'content': content, 'policy_type': policy_type})


def terms(request):
    return _render_policy(request, '이용약관', getattr(settings, 'TERMS_DOC_PATH', ''), policy_type='terms')


def privacy(request):
    return _render_policy(request, '개인정보 처리방침', getattr(settings, 'PRIVACY_DOC_PATH', ''), policy_type='privacy')


@login_required
def reconsent(request):
    # 이미 최신 버전이면 next로 바로 보내기
    if request.user.terms_version == getattr(settings, 'TERMS_VERSION', None) and \
       request.user.privacy_version == getattr(settings, 'PRIVACY_VERSION', None):
        next_url = request.GET.get('next') or request.POST.get('next') or '/'
        return redirect(next_url)

    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    form = ReconsentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(request.user)
        messages.success(request, '약관 및 개인정보 처리방침에 동의가 완료되었습니다.')
        return redirect(next_url)

    return render(request, 'reconsent.html', {
        'form': form,
        'next': next_url,
        'terms_url': getattr(settings, 'TERMS_URL', '#'),
        'privacy_url': getattr(settings, 'PRIVACY_URL', '#'),
    })
