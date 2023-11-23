from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AssesmentForm

# Create your views here.
@login_required
def greeting(request):
    form = AssesmentForm()# To allow users to create a new assesment 
    return render(request, "base/home_screen.html", {"form": form})

@login_required
def create_assesment(request):
    pass

def bink_test(request):
    return render(request, "base/temp_bink.html")