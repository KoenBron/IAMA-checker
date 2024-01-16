from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User

# Simple forms to register and log in users

class RegisterForm(UserCreationForm):
    # Alter widget settings by overriding them in the init function
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Give the proper class
        self.fields["password1"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["password2"].widget = forms.PasswordInput(attrs={"class": "form-control"})

    username = UsernameField(widget=(forms.TextInput(attrs={"class": "form-control"})))


class UserLoginForm(AuthenticationForm):
    username = UsernameField(widget=(forms.TextInput(attrs={"class": "form-control"})))
    password = forms.CharField(widget=(forms.PasswordInput(attrs={"class": "form-control"})))
