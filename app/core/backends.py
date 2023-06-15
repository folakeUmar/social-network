from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from django.db.models import Q


class CustomBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        username = email

        try:
            user = get_user_model().objects.filter(
                 Q(email__iexact=username)
            ).first()

            if user and user.check_password(password):
                return user
            return None
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id, **kwargs):
        UserModel = get_user_model()
        try:
            user = get_user_model()._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None