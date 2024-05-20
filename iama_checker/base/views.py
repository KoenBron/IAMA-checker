from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AssesmentForm, AnswerForm, CollaboratorForm, SearchEditorForm, LawForm
from .models import Assesment, Question, Answer, Collaborator, Reference, Law
from django.contrib.auth.models import User 
from django.http import HttpResponseRedirect 
from django.urls import reverse
from .base_view_helper import * 

# Create your views here.
@login_required
def home(request):
    # Get all the assesments associated to the logged in user en present them descendingly
    assesments_list = Assesment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
    assesments_editor_list = request.user.related_assesment.all()
    return render(request, "base/home.html", {"assesments_list": assesments_list, "assesments_editor_list": assesments_editor_list})

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
            # Get all the assesments associated to the logged in user en present them descendingly
            assesments_list = Assesment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
            return render(request, "base/home.html", {"assesments_list": assesments_list, "error": "Voer valide dat in!"})
    
@login_required
def delete_assesment(request, assesment_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment om te verwijderen bestaat niet!"})

    # Check if the user is autorised to delete the assesment
    if not user_has_edit_privilidge(request.user.pk, assesment):
        return render(request, "errors/error.html", {"message": "Gebruiker is niet toegestaan om deze assesment te verwijderen!"})    

    else:
        assesment.delete()
        return HttpResponseRedirect(reverse("base:home"))

# Update the info of a single assesment
@login_required
def update_assesment(request, assesment_id):
    # Make sure it's a post request
    if request.method == "POST":
        # Check whether the assesment exists and if so make sure the user has edit privilidges
        try:
            assesment = Assesment.objects.get(pk=assesment_id)
        except (KeyError, Assesment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assesment om te updaten bestaat niet!"})

        if not user_has_edit_privilidge(request.user.pk, assesment):
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen permissie om deze assesment te updaten!"})

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

# Retreives the desired assignment and global assesment info
@login_required
def detail(request, assesment_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    # Couldn't retrieve the assesment from the db
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment bestaat niet!"})
    
    if not user_has_edit_privilidge(request.user.pk, assesment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})

    # Get the lists with the context for the pages
    index_context_objects = {
        "question_list": Question.objects.exclude(question_phase=5).order_by("pk"),
        "status_list": get_complete_status(request, assesment),
        "editor_list": assesment.user_group.all(),
    }

    return render(request, "base/detail.html", {"assesment": assesment, "index_context_objects": index_context_objects})

# Retrieves the details of a question or phase introduction
# TODO: At some point fix this clusterfuck of a function
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
    if not user_has_edit_privilidge(request.user.pk, assesment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})

    # Id's of next and next questions
    buttons = {
        "next": question.id + 1,
        "prev": question.id - 1
    }
    
    # Objects need te render the question index correctly
    index_context_objects = {
        "question_list": Question.objects.exclude(question_phase=5).order_by("pk"),
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
        context = {
            "assesment": assesment, 
            "question": question, 
            "index_context_objects": index_context_objects, 
            "buttons": buttons,
            "reference_list": Reference.objects.filter(questions=question),
            "jobs": question.jobs_as_py_list(),
        }

        # Phase 4 intro is special and needs to list all the laws that are endangered according to the assesment
        if question.question_phase == 4:
            context["law_list"] = Law.objects.filter(assesment=assesment).order_by("name")
            if "error" in request.session:
                context["error"] = request.session["error"]
                del request.session["error"]
            return render(request, "base/q_detail_phase4.html", context)

        # Check if there is already an answer
        try:
            answer = Answer.objects.filter(question_id=question.pk, user__pk=request.user.pk, assesment_id=assesment.id).latest("created")
            # Create an empty answer and save it, NOTE: not really necessary, but afraid of possible unexpected behaviour if removed
        except (KeyError, Answer.DoesNotExist):
            answer = Answer(assesment_id=assesment, question_id=question, user=request.user, status=Answer.Status.UA)
            answer.save()

        # Add necessary context for questions that are not in phase 4
        context["answer"] = answer
        context["collab_list"] = Collaborator.objects.filter(answers=answer)
        context["collab_options"] = get_collab_options(assesment, answer)
        context["questions_history"] = get_answers_sorted(assesment, question)

        return render(request, "base/q_detail.html", context)

# Save an answer to the database and alter it's completion status
@login_required
def save_answer(request, assesment_id, question_id):    

    if request.method == "POST":
        # Retrieve answer and assesment from the database
        try:
            assesment = Assesment.objects.get(pk=assesment_id)
            question = Question.objects.get(pk=question_id)
            answer = Answer.objects.filter(assesment_id=assesment, question_id=question).latest("created")

        except (KeyError, Answer.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Opgeslagen antwoord is niet gevonden in de db!"})
        
        except (KeyError, Assesment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assesment kan niet gevond worden!"})

        except (KeyError, Question.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Vraag kan niet gevond worden!"})

        # Check if user is autorised
        if not user_has_edit_privilidge(request.user.pk, assesment):
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})
        
        # Put the POST request data into form
        answer_form = AnswerForm(request.POST)

        # Make sure the data is valid
        if answer_form.is_valid():

            # Only create a new answer if the answers content has been updated
            if answer_form.data["answer_content"].strip() != answer.answer_content:
                answer = Answer(assesment_id=assesment, user=request.user, question_id=question)

                # Update answer data
                answer.answer_content = answer_form.data["answer_content"].strip()# is_valid drops answer content from cleaned data?????

            # Check the state of the question

            # Unanswered
            if answer_form.data["answer_content"] == "":# is_valid drops answer content from cleaned data?????
                answer.status = Answer.Status.UA

            # Reviewed
            elif answer_form.cleaned_data["reviewed"]:
                answer.status = Answer.Status.RV

            # Answered
            else:
                answer.status = Answer.Status.AW

            answer.save()

            # Only reverse the stored completion status when the return value indicates a change in completion
            assesment.complete_status = all_answers_reviewed(assesment_id)
            assesment.save()
                 
            # Return to question detail page with updated answer
            return HttpResponseRedirect(reverse("base:question_detail", args=(assesment_id, question_id,)))

        # Error
        else:
            return render(request, "errors/error.html", {"message": "Voer valide data in!"})

# Add an existing collaborator to a question
@login_required
def add_collab(request, answer_id, collab_id):
    # Get the answer, assesment and collaborator
    try:
        answer = Answer.objects.get(pk=answer_id)
        collab = Collaborator.objects.get(pk=collab_id)
        assesment = Assesment.objects.get(pk=answer.assesment_id.id)

    except (KeyError, Answer.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker aan toe te voegen kan niet in database gevonden worden!"})
    
    except (KeyError, Collaborator.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker aan toe te voegen kan niet in database gevonden worden!"})
    
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment kan niet gevond worden!"})

    # Check if user is autorised
    if not user_has_edit_privilidge(request.user.pk, assesment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})

    # Add it to the many-to-many relation
    answer.collaborator_set.add(collab)

    return HttpResponseRedirect(reverse("base:question_detail", args=(answer.assesment_id.id, answer.question_id.id,)))

# Create a collaborator and add it to the current question
@login_required
def create_add_collab(request, answer_id):
    if request.method == "POST":
        # Get the answer and assesment
        try:
            answer = Answer.objects.get(pk=answer_id)
            assesment = Assesment.objects.get(pk=answer.assesment_id.id)

        except (KeyError, Answer.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Kan vraag om medewerker aan toe te voegen niet vinden in de database!"})

        except (KeyError, Assesment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assesment kan niet gevond worden!"})

        # Check if user is autorised
        if not user_has_edit_privilidge(request.user.pk, assesment):
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
    # Get the answer, assesemnt and collab
    try:
        answer = Answer.objects.get(pk=answer_id)
        collab = Collaborator.objects.get(pk=collab_id)
        assesment = Assesment.objects.get(pk=answer.assesment_id.id)

    except (KeyError, Answer.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker van te verwijderen bestaat niet in de database!"})

    except (KeyError, Collaborator.DoesNotExist) :
        return render(request, "errors/error.html", {"message": "Medewerker om van de vraag te verwijderen bestaat niet in de database!"})

    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment kan niet gevond worden!"})

    # Check if user is autorised
    if not user_has_edit_privilidge(request.user.pk, assesment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})

    else:
        # Delete relation and go back to next page
        answer.collaborator_set.remove(collab)

        # Check if there is any answer associated with the collaborator
        if collab.answers is None:
            collab.delete()# No answers associated, delete the collaborator

        return HttpResponseRedirect(request.GET.get("next", "/"))

@login_required
def info(request):
    return render(request, "base/info.html") 

@login_required
def add_editor(request, assesment_id, editor_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment bestaat niet!"})
    
    if user_has_edit_privilidge(request.user.pk, assesment):
        editor = User.objects.get(pk=editor_id)
        assesment.user_group.add(editor)

        # TODO make it so that the page where the user came from is remembered and that the user returns to it
        return HttpResponseRedirect(reverse("base:detail", args=(assesment.id,)))
    
    else:
        return render(request, "errors/error.html", {"message": "Alleen de maker van een assesment kan editors toevoegen!"})

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
            next = request.GET.get("next", reverse("base:detail", args=(assesment.id,)))
            print(request.GET)
            return render(request, "base/search_editor.html", {"assesment": assesment, "next": next})

        """
        This version of adding editors to an assesment is for prototyping only in a controlled environment.
        When creating a more complete software solution, an inbox system should be put into place as to
        prevent people from spam adding them to projects.
        Also the adding of editors now goes by id, which may be subject to change but it will do for the purposes of this prototype.
        """

        # Post request contains the user id and reverts the user to a confirmation screen on wether they really want to add that user
        if request.method == "POST":
            form = SearchEditorForm(request.POST) 
            next = request.POST.get("next", reverse("base:detail", args=(assesment.id,)))

            # First check wether the given value is an integer
            if form.is_valid():

                # Make sure the editor added isn't the same user as the user sending the request
                if request.user.pk == form.cleaned_data["editor_id"]:
                    return render(request, "base/search_editor.html", {"assesment": assesment, "next": next, "error": "Kan jezelf niet als editor toevoegen!"})

                # Find an editor
                try:
                    editor = User.objects.get(pk=form.cleaned_data["editor_id"]) 

                # No user found with entered id
                except (KeyError, User.DoesNotExist):
                    return render(request, "base/search_editor.html", {"assesment": assesment, "next": next ,"error": "Kan geen editor vinden met dit id!"})

                # User found
                return render(request, "base/confirm_editor.html", {"assesment": assesment, "next": next, "editor": editor})
            
            # No integer entered
            else:
                return render(request, "base/search_editor.html", {"assesment": assesment, "next": next, "error": "Ingevoerde waarde moet een heel nummer zijn!"})
                
@login_required
def delete_editor(request, assesment_id, editor_id):
    # Find the assesment
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
        editor = User.objects.get(pk=editor_id)

    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment bestaat niet!"})
    
    except (KeyError, User.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Editor bestaat niet!"})

    # Check user privilidges
    if user_has_edit_privilidge(request.user.pk, assesment):
        
        # Delete the editor from the assesment en return to detail page
        assesment.user_group.remove(editor)
        return HttpResponseRedirect(reverse("base:detail", args=(assesment.id,)))
    
    else:
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen permissie om editors te verwijderen!"})

@login_required
def landing_page(request):
    return render(request, "base/landing_page.html")

@login_required
def create_law(request, assesment_id):
    if request.method == "POST":
        # Find the assesment
        try:
            assesment = Assesment.objects.get(pk=assesment_id)

        except (KeyError, Assesment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assesment bestaat niet!"})
        
        if not user_has_edit_privilidge(request.user.pk, assesment):
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen permissie om grondrechten toe te voegen!"})
        
        # Retrieve the post data and make it usable 
        form = LawForm(request.POST)
        next = request.POST.get("next", reverse("base:question_detail", args=(assesment.id, 11,)))

        # Validate form data
        if form.is_valid():
            # Create the Law object
            law = Law(name=form.cleaned_data["name"])
            law.assesment = assesment
            law.save()
            return HttpResponseRedirect(next)

        # Form error
        else:
            request.session["error"] = "Gebruiker heeft geen valide data ingevoerd!"
            return HttpResponseRedirect(next)

    else:
        render(request, "errrors/error.html", {"message": "Alleen POST requests zijn toegestaan voor de actie!"})

@login_required
def delete_law(request, law_id):
    if request.method == "GET":
        # Get the law object
        try:
            law = Law.objects.get(pk=law_id)

        except (KeyError, Law.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Grondrecht bestaat niet!"})

        # Check user privilidges
        if not user_has_edit_privilidge(request.user.pk, law.assesment):
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen permissie om grondrechten te verwijderen!"})
        
        # Get the next address to go to after deletion
        next = request.GET.get("next", reverse("base:question_detail", args=(law.assesment.id, 11,)))

        # Delete law object
        law.delete()
        return HttpResponseRedirect(next)

    else:
        render(request, "errrors/error.html", {"message": "Alleen GET requests zijn toegestaan voor de actie!"})

            
@login_required
def law_detail(request, law_id, law_question_id):
    try:
        law = Law.objects.get(pk=law_id)
        question = Question.objects.get(pk=law_question_id) 

    # No law object found in db
    except (KeyError, Law.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Grondrecht bestaat niet!"})

    # No question object found in db
    except (KeyError, Question.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Grondrecht bestaat niet!"})

    # Check user authority 
    if not user_has_edit_privilidge(request.user.pk, law.assesment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assesment!"})

    # Id's of next and next questions
    buttons = {
        "next": question.id + 1,
        "prev": question.id - 1
    }

    # Objects need te render the question index correctly
    index_context_objects = {
        "question_list": Question.objects.exclude(question_phase=5).order_by("pk"),
        "status_list": get_complete_status(request, law.assesment),# TODO: Change this to only get the complete status of the answers for the law questions
    }

    return render(request, "base/q_detail.html")
    
    
