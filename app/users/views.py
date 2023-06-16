from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache.backends.base import DEFAULT_TIMEOUT

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (VerifyTokenSerializer, CustomObtainTokenPairSerializer, CreateUserSerializer, 
                          UserRegisterSerializer, InitializePasswordReesetSerializer, ResetPasswordSerializer)


CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)

# @extend_schema(parameters=[SUBDOMAIN_HEADER])


class CustomObtainTokenPairView(TokenObtainPairView):
    """Login with email and password"""

    serializer_class = CustomObtainTokenPairSerializer


class AuthViewSet(viewsets.ModelViewSet):
    """User ViewSets"""

    queryset = get_user_model().objects.all()
    serializer_class = CreateUserSerializer
    http_method_names = ["get", "post"]
  
    def get_serializer_class(self):
     
        if self.action == 'verify_token':
            return VerifyTokenSerializer
        elif self.action == 'create':
            return CreateUserSerializer
        elif self.action == 'register_user':
            return UserRegisterSerializer   
        elif self.action == 'initialize_reset':
            return InitializePasswordReesetSerializer
        elif self.action == 'reset_password':
            return ResetPasswordSerializer
        return super().get_serializer_class()
    

    @action(
        methods=["POST"],
        detail=False,
        url_path="verify-token",
    )
    def verify_token(self, request, pk=None):
        serializer = self.get_serializer(
            data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['POST'],
        detail=True,
        url_path='register-user',
    )
    def register_user(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=user, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "User registration completed"}, status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['POST'],
        detail=False,
        url_path='initialize_reset',
    )
    def initialize_reset(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )

    @action(
            methods=['POST'],
            detail=False,
            url_path='reset-password',
    )
    def reset_password(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data, instance=user)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )
