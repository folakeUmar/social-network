from django.contrib.auth.base_user import BaseUserManager

from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):


    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError(_("Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if kwargs.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if kwargs.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        user = self.create_user(email, password, **kwargs)
        # to check if user will save in the db with the save command in the create_user()
        # user.save() 
        return user
        