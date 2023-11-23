from django.shortcuts import render
from django.http import HttpResponseRedirect
from .forms import RegisterForm
from django.contrib.auth.models import User

# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
            user.save()
            return HttpResponseRedirect("/")
    else:
        form = RegisterForm

    return render(request, "accounts/register.html", {"form": form})
    