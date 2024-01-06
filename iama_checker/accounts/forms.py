from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username"]

class UserLoginForm(AuthenticationForm):
    # Init with the params of the class it inherits from
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = UsernameField(widget=(forms.TextInput(attrs={"class": "form-control"})))
    password = forms.CharField(widget=(forms.PasswordInput(attrs={"class": "form-control"})))