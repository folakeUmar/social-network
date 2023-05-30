import uuid
from datetime import datetime, timezone

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from core.models import AuditableModel
from core import settings
from .manager import CustomUserManager
from .enums import CITIES, PROFESSIONS


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    preferred_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True)
    pin = models.CharField(max_length=15)
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


    class Profile(AuditableModel):
        user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        image = models.FileField(upload_to='userphoto/', blank=True, null=True)
        date_of_birth = models.CharField(max_length=255)
        recognition_year = models.CharField(max_length=255)
        professional_field = models.CharField(max_length=255, choices=PROFESSIONS)
        location = models.CharField(max_length=255, choices=CITIES)
        bio = models.TextField()
        
        class Meta:
            ordering = ('-created_at', )

            def __str__(self):
                return str(self.user)
            
