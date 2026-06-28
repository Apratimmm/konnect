from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class Media(models.Model):

    def upload_to(instance, filename):
        return f'{instance.username}/{filename}'

    username=models.CharField(max_length=30)
    room=models.CharField(max_length=30)
    file = models.FileField(upload_to=upload_to)
    media_type = models.CharField(max_length=10)

class UserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()

class User(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user_info'

class in_call(models.Model):
    username = models.CharField(max_length=30, unique=True)
    room = models.CharField(max_length=20)

    class Meta:
        db_table = 'in_call'

class OTPVerification(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=1)

    class Meta:
        db_table = 'otp_table'