from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.urls import reverse
# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
            # Invalid input so jump back to register page 
            if user is None:
                error = "Invoer is incorrect!"

            else:
                user.save()
                # Log the user in and send him to his home screen
                login(request, user)
                return HttpResponseRedirect(reverse("base:home"))
        # The is_valid() returns false if password1 and password2 don't match, src=https://docs.djangoproject.com/en/1.8/_modules/django/contrib/auth/forms/
        else:
            error = "De ingevoerde wachtwoorden komen niet overeen!"
    
    form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form, "error": error})
    
