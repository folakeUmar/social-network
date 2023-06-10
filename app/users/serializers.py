from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from email_validator import validate_email, EmailNotValidError
 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers, exceptions

from .models import User

from .utils import generate_otp
from .tasks import user_code_email
class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        if not user.verified and not user.is_active:
            raise exceptions.AuthenticationFailed(
                _("Account Deactivated."), code="authentication"
            )
        token = super().get_token(user)
        if not user.verified:
            raise exceptions.AuthenticationFailed(
                _("Account not yet verified."), code="authentication"
            )

        # Add custom claims
        token.id = user.id
        token["email"] = user.email
        token["preferred_name"] = user.firstname
        return token


class VerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs['email'].lower().strip()
        if get_user_model().object.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists')
        try:
            valid = validate_email(attrs['email'])
            attrs['email'] = valid.email
            return super().validate(attrs)
        except EmailNotValidError as e:
            raise serializers.ValidationError(e)
        return super().validate(attrs)


    def create(self, validated_data):
        email = validated_data['email']
        user = User.object.create(email=email)
        code = generate_otp()
        print(code)
        email = validated_data.get('email')
        user_data = {'email': email, 'code': code,
                     'url': f"{settings.CLIENT_URL}/register/"}    
        user_code_email.delay(user_data)
        return user
    

class CreateUserSerializer(serializers.ModelSerializer):
    code = serializers.IntegerField(required=True)

    class Meta:
        model = get_user_model()
        fields = "__all__"
        extra_kwargs = {
            'email': {'read_only': True},
        }

    def validate(self, attrs):
        return super().validate(attrs)