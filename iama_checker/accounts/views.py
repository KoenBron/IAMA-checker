from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.urls import reverse
# Create your views here.
def register(request):
    # Create placeholders  
    context = {}
    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
            # No username given 
            except ValueError:
                context["error"] = "Er moet een gebruikersnaam ingevoerd worden!"
            
            # User can safely be created, on checking for double user credentials yet!
            else:
                user.save()
                # Log the user in and send him to his home screen
                login(request, user)
                return HttpResponseRedirect(reverse("base:home"))

        # The is_valid() returns false if password1 and password2 don't match, src=https://docs.djangoproject.com/en/1.8/_modules/django/contrib/auth/forms/
        else:
            context["error"] = "De ingevoerde wachtwoorden komen niet overeen!" 

    context["form"] = form 
    return render(request, "accounts/register.html", context)
    
