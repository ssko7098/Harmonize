from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError
import os 

# Create your models here.
class CustomAccountManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError(('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=30)
    email = models.EmailField(("email address"),
                              max_length=30,
                              unique=True,
                              error_messages={
                              "unique": ("A user with that email address already exists."),
                              },
                              )
    
    password = models.CharField(max_length=30)
    is_admin = models.BooleanField(default=False,
                                   help_text=("Designates whether the user can log into this admin site.")
                                   )
    
    is_active = models.BooleanField(default=True,
                                    help_text=("Designates whether this user should be treated as active. Unselect this instead of deleting accounts.")
                                    )
    
    is_verified = models.BooleanField(default=False,
                                    help_text=("Designates whether this user has verified their email address.")
                                    )
    
    date_joined = models.DateTimeField(("date joined"), default=timezone.now)

    objects = CustomAccountManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = [] # username and password are required by default

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        return self.is_admin

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    avatar_file = models.FileField(upload_to='avatars/', null=True, blank=True)
    report_count = models.PositiveIntegerField(default=0)

    reported_by = models.ManyToManyField(User, related_name='reported_profiles', blank=True)

    def __str__(self):
        return self.user.username
    
    def clean(self):
        if self.avatar_file and not self.avatar_file.name.endswith(('.jpg', '.jpeg')):
            raise ValidationError('Only JPEG files are allowed.')
        
    def delete(self, *args, **kwargs):
        # Delete the jpg file from storage
        if self.avatar_file and os.path.isfile(self.avatar_file.path):
            os.remove(self.avatar_file.path)

        # Call the parent class's delete method to delete the Profile instance
        super(Profile, self).delete(*args, **kwargs)