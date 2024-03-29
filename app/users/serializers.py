from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.contrib.auth.hashers import make_password

from email_validator import validate_email, EmailNotValidError
 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers, exceptions

from .models import User, Token
from .enums import USER_PROFESSIONS, CITIES
from .utils import generate_code
from .tasks import user_code_email, send_password_reset_email


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
        token["preferred_name"] = user.first_name
        return token


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs['email'].lower().strip()
        if get_user_model().objects.filter(email=email).exists():
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
        user = User.objects.create(email=email)
        user.save()
        token = Token.objects.create(token=token, user=user)
        user_data = {'email': email, 'token': token.token,
                     'url': f"{settings.CLIENT_URL}/register/"}
        print(token.token)   
        user_code_email.delay(user_data)
        return user
    

class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'


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
        return user


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    professional_field = serializers.ChoiceField(choices=USER_PROFESSIONS, required=False)
    location = serializers.ChoiceField(choices=CITIES, required=False)

    class Meta:
        model = get_user_model()
        fields = '__all__'
        extra_kwargs = {
            'email': {'read_only': True},
            'is_active': {'read_only': True},
            'is_staff': {'read_only': True},
            'last_login': {'read_only': True},
            'created_at': {'read_only': True},
            'verified': {'read_only': True},
            'group': {'read_only': True},
        }
    
    def update(self, instance, validated_data):
        password = validated_data['password']
        super().update(instance, validated_data)
        instance.set_password(password)
        instance.save()
        return instance
   

class InitializePasswordReesetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs['email'].lower().strip()
        email = get_user_model().objects.filter(email=email).first()
        attrs['email'] = email
        active_user = self.context['request'].user.is_active
        if not email:
            return serializers.ValidationError('Email does not exist')
        if not active_user:
            return serializers.ValidationError('No active user found')
        return super().validate(attrs)

    def create(self, validated_data):
        email = validated_data['email']
        user = self.context['request'].user
        token = generate_code()
        token, created = Token.objects.update_or_create(user=user, token_type='PASSWORD_RESET', token=token)
        token.save()
        email_data = {'fullname': user.first_name,
                        'email': user.email,
                        'token': token.token,
                        'url': f"{settings.CLIENT_URL}/passwordreset/?token={token.token}",
        }
        print(token.token)
        send_password_reset_email.delay(email_data)
        return user



class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def to_representation(self, instance):
        return CreateUserSerializer(instance).data
    
    def validate(self, attrs):
        token = attrs['token']
        token = Token.objects.filter(token=token).first() 
        password = attrs['password']
        confirm_password = attrs['confirm_password']
        if not token:
            raise serializers.ValidationError("Invalid Token!")
        attrs['token'] = token   
        if password != confirm_password:
            raise serializers.ValidationError('Passwords do not match!')
        return super().validate(attrs)

    def update(self, instance, validated_data):
        password = validated_data['password']
        instance.set_password(password)
        instance.save()
        # super().update(instance, validated_data)
        return instance
    