from django.contrib.auth import login as auth_login, logout as auth_logout
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSignupSerializer

@api_view(["POST"])
@permission_classes([AllowAny])
@parser_classes([JSONParser, FormParser, MultiPartParser])
def signup(request):
    serializer = UserSignupSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    auth_login(request, user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)