from rest_framework_simplejwt.views import TokenObtainPairView

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import VerificationCodeSerializer, CustomObtainTokenPairSerializer, CreateUserSerializer


CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)

# @extend_schema(parameters=[SUBDOMAIN_HEADER])


class CustomObtainTokenPairView(TokenObtainPairView):
    """Login with email and password"""

    serializer_class = CustomObtainTokenPairSerializer


class AuthViewSet(viewsets.ModelViewSet):
    """User ViewSets"""

    queryset = get_user_model().object.all()
    serializer_class = VerificationCodeSerializer
    http_method_names = ["get", "post"]
  
    def get_serializer_class(self):
     
        if self.action == 'send_code':
            return VerificationCodeSerializer
        # elif self.action == 'create':
        #     return CreateUserSerializer   
        return super().get_serializer_class()
    

    @action(
        methods=["POST"],
        detail=False,
        url_path="send-code",
    )
    def send_code(self, request, pk=None):
        serializer = self.get_serializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "data": serializer.data}, status=status.HTTP_200_OK
            )
        return Response(
            {"success": False, "errors": serializer.errors}, status.HTTP_400_BAD_REQUEST
        )
