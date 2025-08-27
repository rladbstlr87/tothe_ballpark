from django.contrib.auth import get_user_model, password_validation
from rest_framework import serializers

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "email",
            "nickname",
            "team",
            "profile_image",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "nickname": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "team": {
                "required": False,
                "allow_null": True,
            },
            "profile_image": {
                "required": False,
            },
        }
    
    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value
    
    def validate(self, attrs):
        attrs = super().validate(attrs)
        username = attrs.get("username")
        email = attrs.get("email")

        if username and User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "이미 사용 중입니다."})
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "이미 사용 중입니다."})
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user