from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AssesmentForm
from .models import Assesment, Question
from django.http import HttpResponseRedirect, HttpResponse

import json

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

# Update the info of a single assesment
@login_required
def update_assesment(request, assesment_id):
    # Make sure it's a post request
    if request.method == "POST":
        try:
            assesment = Assesment.objects.filter(user__pk=request.user.pk, id=assesment_id)
        except (KeyError, Assesment.DoesNotExist):
            return HttpResponse("Assesment doesn't exist, 404 page comes later")
        # Create a form to easily validate and extract the data
        form = AssesmentForm(request.POST)
        if form.is_valid():
            # We don't use the update() method so the assesment.date_last_saved value is newly set
            assesment.name = form.cleaned_data['name']
            assesment.organisation = form.cleaned_data['organisation']
            assesment.save()
            # Return back to the page where it came from
            return HttpResponseRedirect(request.path)
        else:# Return error
            return HttpResponse("Error updating data, 404 page comes later")

# Retreives the desired assignment
@login_required
def detail(request, assesment_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    # Couldn't retrieve the assesment from the db
    except (KeyError, Assesment.DoesNotExist):
        return HttpResponse("Page doesn't exist, 404 page comes later")
    
    # Background colors for phase intro list items, in case of more phases also set new colors or the code breaks!
    color = [
        "#007bc760",
        "#42145f60",
        "#a9006160",
        "#ffb61260"
    ]
    # Create a list of dicts of with the questions seperated by phase
    current_phase = 1# Counter
    questions = []# List to append
    # Go through each phase and retrieve the questions
    while (question_list := Question.objects.filter(question_phase=current_phase).order_by("question_number")):
        questions.append({"phase": current_phase, "question_list": question_list, "list_item_color": color[current_phase - 1]})
        current_phase += 1

    return render(request, "base/detail.html", {"assesment": assesment, "questions": questions})

@login_required
def phase_intro(request, assesment_id, phase):
    return render(request, "base/phase_intro.html")

@login_required
def question_detail(request, assesment_id, question_id):
    return HttpResponse("New datai page!")

def bink_test(request):
    return render(request, "base/temp_bink.html")