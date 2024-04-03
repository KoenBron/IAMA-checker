from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AssesmentForm, AnswerForm, CollaboratorForm, SearchEditorForm
from .models import Assesment, Question, Answer, Collaborator, Reference
from django.contrib.auth.models import User 
from django.http import HttpResponseRedirect 
from django.urls import reverse
from .base_view_helper import * 

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
            assesment = Assesment(name=form.cleaned_data['name'].strip(), organisation=form.cleaned_data['organisation'].strip(), ultimately_responsible=form.cleaned_data['ultimately_responsible'].strip(), user=request.user)
            assesment.save()
            
            # Create empty answers to ensure correct and predictable behaviour
            generate_empty_answers(assesment, request.user)
            
            # Go to the detail page of the new assignment
            return HttpResponseRedirect(reverse("base:detail", args=(assesment.id,)))

        else:
            print(form.errors)
            # Get all the assesments associated to the logged in user en present them descendingly
            assesments_list = Assesment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
            return render(request, "base/home.html", {"assesments_list": assesments_list, "error": "Voer valide dat in!"})
    
@login_required
def delete_assesment(request, assesment_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment om te verwijderen bestaat niet!"})

    # Check if the user that deletes is the same user that has authority to delete this assesment
    if request.user.pk != assesment.user.pk:
        return render(request, "errors/error.html", {"message": "Gebruiker is niet toegestaan om deze assesment te verwijderen!"})    

    else:
        assesment.delete()
        return HttpResponseRedirect(reverse("base:home"))

# Update the info of a single assesment
@login_required
def update_assesment(request, assesment_id):
    # Make sure it's a post request
    if request.method == "POST":
        try:
            assesment = Assesment.objects.get(user__pk=request.user.pk, id=assesment_id)
        except (KeyError, Assesment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assesment om te updaten bestaat niet!"})

        # Create a form to easily validate and extract the data
        form = AssesmentForm(request.POST)
        if form.is_valid():
            # We don't use the update() method so the assesment.date_last_saved value is newly set
            assesment.name = form.cleaned_data['name'].strip()
            assesment.organisation = form.cleaned_data['organisation'].strip()
            assesment.ultimately_responsible = form.cleaned_data['ultimately_responsible'].strip()
            assesment.save()
            # Return back to the detail page
            return HttpResponseRedirect(reverse("base:detail", args=(assesment_id,)))
        # No valid data in the form so need to add error as argument to render
        else:
            return render(request, "errors/error.html", {"message": "Geen valide invoer om de assesment te update!"})

# Retreives the desired assignment
@login_required
def detail(request, assesment_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    # Couldn't retrieve the assesment from the db
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment bestaat niet!"})
    
    if request.user.pk != assesment.user.pk:
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})
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
        return render(request, "errors/error.html", {"message": "Assesment bestaat niet!"})
    
    # Couldn't retrieve the question from the db
    except (KeyError, Question.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Verzochte vraag van deze assesment bestaat niet!"})
     
    # Check user authority 
    if request.user.pk != assesment.user.pk:
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})
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
            # Get the references for all of the questions associated with a the requested phase
            "reference_list": Reference.objects.filter(questions__question_phase=question.question_phase),
            "jobs": jobs_per_phase(question.question_phase),
        }
        return render(request, "base/phase_intro.html", context)
    
    # Render question_detail page
    else:
        # Check if there is already an answer
        try:
            answer = Answer.objects.get(question_id=question.pk, user__pk=request.user.pk, assesment_id=assesment.id)
            # Create an empty answer and save it, NOTE: not really necessary, but afraid of possible unexpected behaviour if removed
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
            "collab_options": get_collab_options(assesment, answer),
            "jobs": question.jobs_as_py_list(),
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
            assesment = Assesment.objects.get(pk=assesment_id)
        except (KeyError, Answer.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Opgeslagen vraag is niet gevonden in de db!"})
        
        except (KeyError, Assesment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assesment kan niet gevond worden!"})

        # Check if user is autorised
        if request.user.pk != assesment.user.pk:
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})
        
        # Put the POST request data into form
        answer_form = AnswerForm(request.POST)
        # Make sure the data is valid
        if answer_form.is_valid():
            # Update answer data
            answer.answer_content = answer_form.data["answer_content"].strip()# is_valid drops answer content from cleaned data?????

            # Check for empty string as this can reset the completion status of an answer
            if answer_form.data["answer_content"] == "":# is_valid drops answer content from cleaned data?????
                answer.status = Answer.Status.UA

            # Get the reviewed status and mark answer reviewed if checked
            elif answer_form.cleaned_data["reviewed"]:
                answer.status = Answer.Status.RV

            else:
                answer.status = Answer.Status.AW

            answer.save()

            # Only reverse the stored completion status when the return value indicates a change in completion
            if all_answers_reviewed(assesment_id) != assesment.complete_status:
                assesment.complete_status = not assesment.complete_status
                assesment.save()
                 
            # Return to question detail page with updated answer
            return HttpResponseRedirect(reverse("base:question_detail", args=(assesment_id, question_id,)))
        # Error
        else:
            return render(request, "errors/error.html", {"message": "Assesment kan niet gevond worden!"})

# Add an existing collaborator to a question
@login_required
def add_collab(request, answer_id, collab_id):
    # Get the answer and collaborator
    try:
        answer = Answer.objects.get(pk=answer_id)
        collab = Collaborator.objects.get(pk=collab_id)

    except (KeyError, Answer.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker aan toe te voegen kan niet in database gevonden worden!"})
    
    except (KeyError, Collaborator.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker aan toe te voegen kan niet in database gevonden worden!"})
    
    # Check if user is autorised
    if request.user.pk != answer.user.pk:
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})

    # Add it to the many-to-many relation
    answer.collaborator_set.add(collab)

    return HttpResponseRedirect(reverse("base:question_detail", args=(answer.assesment_id.id, answer.question_id.id,)))

# Create a collaborator and add it to the current question
@login_required
def create_add_collab(request, answer_id):
    if request.method == "POST":
        try:
            answer = Answer.objects.get(pk=answer_id)
        except (KeyError, Answer.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Kan vraag om medewerker aan toe te voegen niet vinden in de database!"})

        # Check if user is autorised
        if request.user.pk != answer.user.pk:
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})
        
        # Create a form for validation
        form = CollaboratorForm(request.POST)
        if form.is_valid():
            # Create new collaborator
            collab = Collaborator(name=form.cleaned_data["name"].strip(), discipline=form.cleaned_data["discipline"].strip(), organisation=form.cleaned_data["organisation"].strip())
            collab.save()
            # Add it to an answer
            collab.answers.add(answer)
            return HttpResponseRedirect(request.POST.get("next", "/"))
        # Error
        else:
            return render(request, "errors/error.html", {"message": "Invalide data opgegeven door gebruiker!"})

@login_required
def delete_collab(request, answer_id, collab_id):
    try:
        answer = Answer.objects.get(pk=answer_id)
        collab = Collaborator.objects.get(pk=collab_id)
    # No answer found
    except (KeyError, Answer.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker van te verwijderen bestaat niet in de database!"})
    # No collaborator found
    except (KeyError, Collaborator.DoesNotExist) :
        return render(request, "errors/error.html", {"message": "Medewerker om van de vraag te verwijderen bestaat niet in de database!"})

    # Check if user is autorised
    if request.user.pk != answer.user.pk:
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})

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
        return render(request, "errors/error.html", {"message": "Gebruiker is niet geauthoriseerd om deze bewerking te doen!"})

@login_required
def info(request):
    return render(request, "base/info.html") 

@login_required
def add_editor(request, assesment_id, editor_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment bestaat niet!"})
    
    if user_has_edit_privilidge(request.user.id, assesment):
        editor = User.objects.get(pk=editor_id)
        assesment.user_group.add(editor)
        # TODO make it so that the page where the user came from is remembered and that the user returns to it
        return render(request, "base:detail", {"assesment": assesment})

# Add an editor with editing priviledges to an assesment
@login_required 
def search_editor(request, assesment_id):
    # Find the assesment
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment bestaat niet!"})

    if user_has_edit_privilidge(request.user.id, assesment):
        # Get request shows only the search_page with an form to search for users by id
        if request.method == "GET":
            return render(request, "base/search_editor.html", {"assesment": assesment})

        """
        This version of adding editors to an assesment is for prototyping only in a controlled environment.
        When creating a more complete software solution, an inbox system should be put into place as to
        prevent people from spam adding them to projects.
        Also the adding of editors now goes by id, which may be subject to change but it will do for the purposes of this prototype.
        """

        # Post request contains the user id and reverts the user to a confirmation screen on wether they really want to add that user
        if request.method == "POST":
            form = SearchEditorForm(request.POST) 
            # First check wether the given value is an integer            form = SearchEditorForm(request.POST)
            if form.is_valid():
                # Find an editor
                try:
                    editor = User.objects.get(pk=form.cleaned_data["editor_id"]) 

                # No user found with entered id
                except (KeyError, User.DoesNotExist):
                    return render(request, "base/search_editor.html", {"assesment": assesment, "error": "Kan geen editor vinden met dit id!"})

                # User found
                return render(request, "base/confirm_editor.html", {"assesment": assesment, "editor": editor})
            
            # No integer entered
            else:
                return render(request, "base/search_editor.html", {"assesment": assesment, "error": "Ingevoerde waarde moet een heel nummer zijn!"})
                





@login_required
def landing_page(request):
    return render(request, "base/landing_page.html")
