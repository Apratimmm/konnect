from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields =['username','email']

class UserLoginForm(AuthenticationForm):
    pass