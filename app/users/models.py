import uuid
import random

from datetime import datetime, timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from core.models import AuditableModel
from core import settings
from .manager import CustomUserManager
from .enums import CITIES, PROFESSIONS, TOKEN_TYPE
from .utils import generate_code


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    preferred_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True)
    image = models.FileField(upload_to='userphoto/', blank=True, null=True)
    date_of_birth = models.CharField(max_length=255)
    recognition_year = models.CharField(max_length=255)
    professional_field = models.CharField(max_length=255, choices=PROFESSIONS)
    location = models.CharField(max_length=255, choices=CITIES)
    bio = models.TextField()
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =[]

    object = CustomUserManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.email

        
    def save_last_login(self):
        self.last_login = datetime.now(timezone.utc)
        self.save()

    @property
    def status(self):
        if self.is_active and self.verified:
            return 'ACTIVE'
        elif not self.is_active and self.verified:
            return 'DEACTIVATED'
        elif not self.is_active and not self.verified:
            return 'PENDING'
    

class Token(AuditableModel):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=225, null=True)
    token_type = models.CharField(max_length=255, choices=TOKEN_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return f"{str(self.user)} {self.token}"

    def is_valid(self):
        lifespan_in_seconds = float(settings.TOKEN_LIFESPAN * 60 * 60)
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

    def verify_user(self):
        self.user.verified = True
        self.user.is_active = True
        self.user.save()

    def generate(self):
        if not self.token:
            self.token = generate_code()
            self.save()
