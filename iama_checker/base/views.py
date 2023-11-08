from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.
def redirect(request):
    return HttpResponseRedirect(reverse("base:greeting", args=()))

def greeting(request):
    return render(request, "base/temp_list.html")

def bink_test(request):
    return render(request, "base/temp_bink.html")
