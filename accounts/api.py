from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from .models import User
import random
import string


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    terms_agree = serializers.BooleanField()
    privacy_agree = serializers.BooleanField()

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "password2",
            "nickname",
            "email",
            "team",
            "terms_agree",
            "privacy_agree",
        ]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        if not attrs.get("terms_agree") or not attrs.get("privacy_agree"):
            raise serializers.ValidationError("두 항목 모두 동의하지 않으면 서비스 이용이 어렵습니다.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2", None)
        validated_data.pop("terms_agree", None)
        validated_data.pop("privacy_agree", None)
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.terms_version = getattr(settings, "TERMS_VERSION", None)
        user.privacy_version = getattr(settings, "PRIVACY_VERSION", None)
        now = timezone.now()
        user.terms_agreed_at = now
        user.privacy_agreed_at = now
        user.set_password(password)
        user.save()
        return user


class SignupAPIView(APIView):
    """
    POST /api/accounts/signup/
    """

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"id": user.id, "username": user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- 공통 유틸 및 상태 (API 전용) ---

API_VERIFICATION_CODES = {}
API_VERIFIED_USERS = set()


def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


# --- 중복 확인 ---

class DuplicateCheckAPIView(APIView):
    """
    POST /api/accounts/check-duplicate/
    body: { "field": "username"|"nickname", "value": "<string>" }
    """

    def post(self, request):
        field = (request.data.get("field") or "").strip()
        value = (request.data.get("value") or "").strip()

        if field not in {"username", "nickname"} or not value:
            return Response(
                {"success": False, "message": "field는 username|nickname 이어야 하며 값이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exists = User.objects.filter(**{field: value}).exists()
        if exists:
            return Response(
                {"success": False, "message": f"{field} 값이 이미 사용 중입니다."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response({"success": True, "message": f"{field} 값은 사용 가능합니다."})


# --- 아이디 찾기 ---

class FindIdAPIView(APIView):
    """
    POST /api/accounts/find-id/
    body: { "email": "<email>" }
    """

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        if not email:
            return Response({"success": False, "message": "이메일을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(email=email)
        if not users.exists():
            return Response({"success": False, "message": "해당 이메일로 등록된 계정이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        usernames = [u.username for u in users]
        username_list = "\n".join(usernames)

        send_mail(
            subject="아이디찾기 결과입니다.",
            message=f"요청하신 이메일로 등록된 아이디 목록입니다.\n\n{username_list}",
            from_email=settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=[email],
        )
        return Response({"success": True, "message": "아이디 목록을 이메일로 발송했습니다."})


# --- 비밀번호 재설정(인증 코드) ---

class PasswordResetRequestAPIView(APIView):
    """
    POST /api/accounts/password/reset/request/
    body: { "username": "...", "email": "..." }
    """

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        email = (request.data.get("email") or "").strip()
        if not username or not email:
            return Response({"success": False, "message": "username과 email을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            return Response({"success": False, "message": "일치하는 계정이 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        code = generate_code(6)
        API_VERIFICATION_CODES[username] = code

        send_mail(
            subject="비밀번호 재설정 인증번호",
            message=f"비밀번호 재설정을 위한 인증번호는 {code} 입니다.",
            from_email=settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=[email],
        )
        return Response({"success": True, "message": "인증번호를 이메일로 전송했습니다."})


class PasswordResetConfirmAPIView(APIView):
    """
    POST /api/accounts/password/reset/confirm/
    body: { "username": "...", "code": "123456" }
    """

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        code = (request.data.get("code") or "").strip()
        if not username or not code:
            return Response({"success": False, "message": "username과 code를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        saved_code = API_VERIFICATION_CODES.get(username)
        if saved_code != code:
            return Response({"success": False, "message": "인증번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        API_VERIFIED_USERS.add(username)
        return Response({"success": True, "message": "인증번호가 확인되었습니다."})


class PasswordResetSetAPIView(APIView):
    """
    POST /api/accounts/password/reset/set/
    body: { "username": "...", "new_password": "...", "confirm_password": "..." }
    """

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        pw1 = request.data.get("new_password")
        pw2 = request.data.get("confirm_password")

        if not username or not pw1 or not pw2:
            return Response({"success": False, "message": "username과 비밀번호를 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

        if username not in API_VERIFIED_USERS:
            return Response({"success": False, "message": "인증이 완료된 사용자가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

        if pw1 != pw2:
            return Response({"success": False, "message": "비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"success": False, "message": "계정을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(pw1)
        user.save()
        API_VERIFIED_USERS.discard(username)
        API_VERIFICATION_CODES.pop(username, None)
        return Response({"success": True, "message": "비밀번호가 변경되었습니다."})
