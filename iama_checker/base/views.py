from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AssesmentForm, AnswerForm, CollaboratorForm
from .models import Assesment, Question, Answer, Collaborator, Reference
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

import json

def get_possible_collaborators(assesment):
    return_collab = []
    # Get all the answers associated with the assesment
    answers = Answer.objects.filter(assesment_id=assesment.pk)

    # Get all the collaborators
    for answer in answers:
        return_collab.append(answer.collaborator_set.all())

    return return_collab

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
                    status = "<span class='badge badge-success badge-pill'>Reviewed</span>"
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
    
    # Id's of next and previous questions
    buttons = {
        "next": question.id + 1,
        "prev": question.id - 1
    }
    
    # Objects need te render the question index correctly
    index_context_objects = {
        "question_list": request.session.get("questions", create_question_list()),
        "status_list": get_complete_status(request, assesment),
    }

    # Render phase intro page
    if question.question_number == 0:
        context = {
            "assesment": assesment, 
            "question": question, 
            "index_context_objects": index_context_objects, 
            "buttons": buttons,
            "reference_list": Reference.objects.filter(questions__question_phase=question.phase),
        }
        return render(request, "base/phase_intro.html", context)
    
    # Render question_detail page
    else:
        # Check if there is already an answer
        try:
            answer = Answer.objects.get(question_id=question.pk, user__pk=request.user.pk, assesment_id=assesment.id)
        # Create an empty answer and save it
        except (KeyError, Answer.DoesNotExist):
            answer = Answer(assesment_id=assesment, question_id=question, user=request.user, status=Answer.Status.UA)
            answer.save()

        context = {
            "assesment": assesment, 
            "question": question, 
            "answer": answer, 
            "index_context_objects": index_context_objects, 
            "buttons": buttons,
            "collab_list": Collaborator.objects.filter(answers=answer),
            "reference_list": Reference.objects.filter(questions=question),
            "possible_collab": get_possible_collaborators(assesment)
        }
        
        return render(request, "base/q_detail.html", context)

# Save an answer to the database and alter it's completion status
@login_required
def save_answer(request, assesment_id, question_id):    
    # Only handle post requests that alter the data
    if request.method == "POST":
        # Retrieve answer from the database
        try:
            answer = Answer.objects.get(question_id=question_id, user__pk=request.user.pk, assesment_id=assesment_id)
        except (KeyError, Answer.DoesNotExist):
            return HttpResponse("Error answer object doesn't exist, something went wrong")# TODO: Get regular 404 page
        
        # Put the POST request data into form
        answer_form = AnswerForm(request.POST)
        # Make sure the data is valid
        if answer_form.is_valid():
            # Update answer data
            answer.answer_content = answer_form.data["answer_content"]# is_valid drops answer content from cleaned data?????

            # Check for empty string as this can reset the completion status of an answer
            if answer_form.data["answer_content"] == "":# is_valid drops answer content from cleaned data?????
                answer.status = Answer.Status.UA

            # Get the reviewed status and mark answer reviewed if checked
            elif answer_form.cleaned_data["reviewed"]:
                answer.status = Answer.Status.RV

            else:
                answer.status = Answer.Status.AW

            answer.save()
            # Return to question detail page with updated answer
            return HttpResponseRedirect(reverse("base:question_detail", args=(assesment_id, question_id,)))
        # Error
        else:
            return HttpResponse("error 404, incorrect data submitted for changing answer")

# Add an existing collaborator to a question
@login_required
def add_collab(request, assesment_id, question_id, answer_id, collab_id):
    return HttpResponse("help")

# Create a collaborator and add it to the current question
@login_required
def create_add_collab(request, assesment_id, question_id, answer_id):
    if request.method == "POST":
        try:
            answer = Answer.objects.get(pk=answer_id)
        except (KeyError, Answer.DoesNotExist):
            return HttpResponse("Error answer doesn't exist") # TODO: Get proper 404 page
        
        # Create a form for validation
        form = CollaboratorForm(request.POST)
        if form.is_valid():
            # Create new collaborator
            collab = Collaborator(name=form.cleaned_data["name"], organisation=form.cleaned_data["organisation"])
            collab.save()
            # Add it to an answer
            collab.answers.add(answer)
            return HttpResponseRedirect(request.POST.get("next", "/"))
        # Error
        else:
            return HttpResponse("Error invalid data added")# TODO: Add the error handling and display it when going back to the question_detail page
    return HttpResponse("help")

@login_required
def delete_collab(request, answer_id, collab_id):
    try:
        answer = Answer.objects.get(pk=answer_id)
        collab = Collaborator.objects.get(pk=collab_id)
    # No answer found
    except (KeyError, Answer.DoesNotExist):
        return HttpResponse("error answer doesn't exist")# TODO: create 404 page
    # No collaborator found
    except (KeyError, Collaborator.DoesNotExist) :
        return HttpResponse("error collaborator doesn't exist")# TODO: create 404 page

    # Check if user has authority to delete this collab
    if request.user.pk == answer.user.pk:
        # Delete relation and go back to previous page
        answer.collaborator_set.remove(collab)
        # Check if there is any answer associated with the collaborator
        if collab.answers is None:
            collab.delete()# No answers associated, delete the collaborator
        return HttpResponseRedirect(request.GET.get("next", "/"))
    # User not authorised
    else:
        return HttpResponse("Error, not allowed to remove this collaborator")#swer TODO: Add error page for this