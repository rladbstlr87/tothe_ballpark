from django.contrib.auth import login as auth_login, logout as auth_logout
from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status, serializers

from .serializers import UserSignupSerializer
from django.views.decorators.csrf import ensure_csrf_cookie

@api_view(["POST"])
@authentication_classes([SessionAuthentication])   # CSRF 검사 강제
@permission_classes([AllowAny])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def signup(request):
    try:
        serializer = UserSignupSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as exc:
        return Response(
            {"detail": "Invalid request.", "errors": exc.detail},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = serializer.save()
    auth_login(request, user)

    # "201" : serializer.data가 id/username/email/nickname/team/profile_image만 포함되도록 시리얼라이저 구성 전제
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_issue(request):
    return Response(status=status.HTTP_204_NO_CONTENT)