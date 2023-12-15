from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AssesmentForm
from .models import Assesment, Question, Answer
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

import json

# Helper function to create question list objects
def create_question_list():
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
    # Fill each subdict with oredered questions
    while (question_list := Question.objects.filter(question_phase=current_phase).order_by("question_number")):
        questions.append({"phase_num": current_phase, "question_list": question_list, "list_item_color": color[current_phase - 1]})
        # Go to the next phase
        current_phase += 1 
    return questions

# Retrieves the completion status as html of every answer related to an assesment
# and puts them in a dictionary that is returned
def get_complete_status(request, assesment):
    question_list = Question.objects.all()
    status_list = {}
    for question in question_list:
        try:
            # Match an answer based on question_id, user_id and assesment_id
            answer = Answer.objects.get(question_id=question.pk, user__pk=request.user.pk, assesment_id=assesment.id)
            status = ""
            match answer.status:
                case Answer.Status.UA:
                    status = "<span class='badge badge-danger badge-pill'>Onbeantwoord</span>"
                
                case Answer.Status.AW:
                    status = "<span class='badge badge-warning badge-pill'>Beantwoord</span>"

                case Answer.Status.RV:
                    status = "<span class='badge badge-succes badge-pill'>Reviewed</span>"
        # Answers are created when the related question_page is first visited so, missing object also means unanswered 
        except (KeyError, Answer.DoesNotExist):
            status = "<span class='badge badge-danger badge-pill'>Onbeantwoord</span>"
        # Append dict
        status_list[str(question.id)] = status

    return status_list
    
# Create your views here.
@login_required
def home(request):
    # Get all the assesments associated to the logged in user en present them descendingly
    assesments_list = Assesment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
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
            # Go to the detail page of the new assignment
            return HttpResponseRedirect(reverse("base:detail", args=(assesment.id,)))
    

# Update the info of a single assesment
@login_required
def update_assesment(request, assesment_id):
    # Make sure it's a post request
    if request.method == "POST":
        try:
            assesment = Assesment.objects.filter(user__pk=request.user.pk, id=assesment_id)[0]
        except (KeyError, Assesment.DoesNotExist):
            return HttpResponse("Assesment doesn't exist, 404 page comes later")
        # Create a form to easily validate and extract the data
        form = AssesmentForm(request.POST)
        if form.is_valid():
            # We don't use the update() method so the assesment.date_last_saved value is newly set
            assesment.name = form.cleaned_data['name']
            assesment.organisation = form.cleaned_data['organisation']
            assesment.save()
            # Return back to the detail page
            return HttpResponseRedirect(reverse("base:detail", args=(assesment_id,)))
        # No valid data in the form so need to add error as argument to render
        else:
            return HttpResponse("Error updating data, 404 page comes later")

# Retreives the desired assignment
@login_required
def detail(request, assesment_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    # Couldn't retrieve the assesment from the db
    except (KeyError, Assesment.DoesNotExist):
        return HttpResponse("Page doesn't exist, 404 page comes later")
    
    # Get the questions as object that is renderable by the template
    question_list = request.session.get("questions", create_question_list())
    # Get the completion statusof each question as a dict
    status_list = get_complete_status(request, assesment)
    
    index_context_objects = {
        "question_list": question_list,
        "status_list": status_list,
    }

    return render(request, "base/detail.html", {"assesment": assesment, "index_context_objects": index_context_objects})

@login_required
def question_detail(request, assesment_id, question_id):
    # Get the desired question and assesment
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
        question = Question.objects.get(pk=question_id)

    # Couldn't retrieve the assesment from the db
    except (KeyError, Assesment.DoesNotExist):
        return HttpResponse("Page doesn't exist, 404 page comes later")
    
    # Create list of dicts from questions
    question_list = request.session.get("questions", create_question_list())

    # Id's of next and previous questions
    buttons = {
        "next": question.id + 1,
        "prev": question.id - 1
    }
    
    # Get the completion status of each answer as a dict
    status_list = get_complete_status(request, assesment)

    index_context_objects = {
        "question_list": question_list,
        "status_list": status_list,
    }

    # Choose whether to render the phase introduction or the detail page of the question 
    if question.question_number == 0:
        return render(request, "base/phase_intro.html", {"assesment": assesment, "question": question, "index_context_objects": index_context_objects, "buttons": buttons})
    else:
        # Check if there is already an answer
        try:
            answer = Answer.objects.get(question_id=question.id)
        # Create an empty answer
        except (KeyError, Answer.DoesNotExist):
            answer = Answer(assesment_id=assesment, question_id=question, user=request.user, status=Answer.Status.UA)
        return render(request, "base/q_detail.html", {"assesment": assesment, "question": question, "answer": answer, "index_context_objects": index_context_objects, "buttons": buttons})
