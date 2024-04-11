from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from . import forms

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("info/", views.info, name="info"),
    path("login/", auth_views.LoginView.as_view(authentication_form=forms.UserLoginForm), name="login")
]
