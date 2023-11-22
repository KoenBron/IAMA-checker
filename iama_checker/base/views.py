from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def greeting(request):
    return render(request, "base/temp_list.html")

def bink_test(request):
    return render(request, "base/temp_bink.html")