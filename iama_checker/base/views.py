from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AssesmentForm
from .models import Assesment
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.
@login_required
def home(request):
    # Get all the assesments associated to the logged in user en present them descendingly
    assesments_list = Assesment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
    form = AssesmentForm()# To allow users to create a new assesment 
    return render(request, "base/home.html", {"assesments_list": assesments_list})


# Create a new assesment
@login_required
def create_assesment(request):
    # Make sure it's a post request
    if request.method == "POST":
        form = AssesmentForm(request.POST)# Create a form to extract information from
        # Make sure all the typed in fields contain valid data
        if form.is_valid():
            # Create assesment object and save to database
            assesment = Assesment(name=form.cleaned_data['name'], organisation=form.cleaned_data['organisation'], user=request.user)
            assesment.save()
            return HttpResponseRedirect("/")# Reload the page to show the newly added assesment

@login_required
def detail(request, assesment_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    except (KeyError, Assesment.DoesNotExist):
        return HttpResponse("Page doesn't exist, 404 page comes later")
    return render(request, "base/detail.html", {"assesment": assesment})

def bink_test(request):
    return render(request, "base/temp_bink.html")