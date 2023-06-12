from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from email_validator import validate_email, EmailNotValidError
 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers, exceptions

from .models import User, Token

from .utils import generate_code
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


class CreateUserSerializer(serializers.Serializer):
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
        token = generate_code()
        user = User.object.create(email=email)
        user.save()
        token = Token.objects.create(token=token, user=user)
        # email = validated_data.get('email')
        user_data = {'email': email, 'token': token.token,
                     'url': f"{settings.CLIENT_URL}/register/"}    
        user_code_email.delay(user_data)
        return user
    

class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

    def to_representation(self, instance):
        return CreateUserSerializer(instance).data


    def validate(self, attrs):
        token = attrs['token']
        token = Token.objects.filter(token=token).first()
        if not token:
            raise serializers.ValidationError("Invalid Token!")
        attrs['token'] = token
        return attrs
        
    def create(self, validated_data):  
        token = validated_data['token']
        user = token.user
        user.verified = True
        user.is_active = True
        user.save()
        print(user.verified, user.is_active)
        return user
