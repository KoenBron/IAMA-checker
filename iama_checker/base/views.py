from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import ContextPopException
from .forms import AssessmentForm, AnswerForm, CollaboratorForm, SearchEditorForm
from .models import Assessment, LawCluster, Question, Answer, Collaborator, Reference
from django.contrib.auth.models import User 
from django.http import HttpResponseRedirect 
from django.urls import reverse
from .base_view_helper import * 

# Create your views here.
@login_required
def home(request):
    # Get all the assessments associated to the logged in user en present them descendingly
    assessments_list = Assessment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
    assessments_editor_list = request.user.related_assessment.all()
    return render(request, "base/home.html", {"assessments_list": assessments_list, "assessments_editor_list": assessments_editor_list})

# Create a new assessment
@login_required
def create_assessment(request):
    # Make sure it's a post request
    if request.method == "POST":
        form = AssessmentForm(request.POST)# Create a form to extract information from
        # Make sure all the typed in fields contain valid data
        if form.is_valid():
            # Create assessment object and save to database
            assessment = Assessment(name=form.cleaned_data['name'].strip(), organisation=form.cleaned_data['organisation'].strip(), ultimately_responsible=form.cleaned_data['ultimately_responsible'].strip(), user=request.user)
            assessment.save()
            
            # Create empty answers to ensure correct and predictable behaviour
            generate_empty_answers(assessment, request.user)
            
            # Go to the detail page of the new assignment
            return HttpResponseRedirect(reverse("base:detail", args=(assessment.id,)))

        else:
            # Get all the assessments associated to the logged in user en present them descendingly
            assessments_list = Assessment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
            return render(request, "base/home.html", {"assessments_list": assessments_list, "error": "Voer valide data in!"})
    
@login_required
def delete_assessment(request, assessment_id):
    try:
        assessment = Assessment.objects.get(pk=assessment_id)
    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment om te verwijderen bestaat niet!"})

    # Check if the user is autorised to delete the assessment
    if not user_has_edit_privilidge(request.user.pk, assessment):
        return render(request, "errors/error.html", {"message": "Gebruiker is niet toegestaan om deze assessment te verwijderen!"})    

    else:
        assessment.delete()
        return HttpResponseRedirect(reverse("base:home"))

# Update the info of a single assessment
@login_required
def update_assessment(request, assessment_id):
    # Make sure it's a post request
    if request.method == "POST":
        # Check whether the assessment exists and if so make sure the user has edit privilidges
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except (KeyError, Assessment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assessment om te updaten bestaat niet!"})

        if not user_has_edit_privilidge(request.user.pk, assessment):
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen permissie om deze assessment te updaten!"})

        # Create a form to easily validate and extract the data
        form = AssessmentForm(request.POST)
        if form.is_valid():
            # We don't use the update() method so the assessment.date_last_saved value is newly set
            assessment.name = form.cleaned_data['name'].strip()
            assessment.organisation = form.cleaned_data['organisation'].strip()
            assessment.ultimately_responsible = form.cleaned_data['ultimately_responsible'].strip()
            assessment.save()
            # Return back to the detail page
            return HttpResponseRedirect(reverse("base:detail", args=(assessment_id,)))
        # No valid data in the form so need to add error as argument to render
        else:
            return render(request, "errors/error.html", {"message": "Geen valide invoer om de assessment te update!"})

# Retreives the desired assignment and global assessment info
@login_required
def detail(request, assessment_id):
    try:
        assessment = Assessment.objects.get(pk=assessment_id)
    # Couldn't retrieve the assessment from the db
    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment bestaat niet!"})
    
    if not user_has_edit_privilidge(request.user.pk, assessment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})

    # Get the lists with the context for the pages
    index_context_objects = {
        "question_list": Question.objects.exclude(question_phase=5).order_by("pk"),
        "status_list": get_complete_status(request, assessment),
        "editor_list": assessment.user_group.all(),
    }

    return render(request, "base/detail.html", {"assessment": assessment, "index_context_objects": index_context_objects})

# Retrieves the details of a question or phase introduction
# TODO: At some point restructure this function
@login_required
def question_detail(request, assessment_id, question_id):
    # Get the desired question and assessment
    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        question = Question.objects.get(pk=question_id)

    # Couldn't retrieve the assessment from the db
    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment bestaat niet!"})
    
    # Couldn't retrieve the question from the db
    except (KeyError, Question.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Verzochte vraag van deze assessment bestaat niet!"})
     
    # Check user authority 
    if not user_has_edit_privilidge(request.user.pk, assessment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})

    # Id's of next and next questions
    buttons = {
        "next": question.id + 1,
        "prev": question.id - 1
    }
    
    # Objects need te render the question index correctly
    index_context_objects = {
        "question_list": Question.objects.exclude(question_phase=5).order_by("pk"),
        "status_list": get_complete_status(request, assessment),
    }

    # Render phase intro page
    if question.question_number == 0:
        context = {
            "assessment": assessment, 
            "question": question, 
            "index_context_objects": index_context_objects, 
            "buttons": buttons,
            "jobs": jobs_per_phase(question.question_phase),
        }

        # Phase 4 intro is special and needs to list all the laws that are endangered according to the assessment
        if question.question_phase == 4:
            # Gather additional context needed for fase 4
            context["jobs"] = jobs_per_phase(4)
            context["law_clusters"] = LawCluster.objects.all()

            if "error" in request.session:
                context["error"] = request.session["error"]
                del request.session["error"]
            return render(request, "base/q_detail_phase4.html", context)

        return render(request, "base/phase_intro.html", context)
    
    # Render question_detail page
    else:
        context = {
            "assessment": assessment, 
            "question": question, 
            "index_context_objects": index_context_objects, 
            "buttons": buttons,
            "reference_list": Reference.objects.filter(questions=question),
            "jobs": question.jobs_as_py_list(),
        }

        # Check if there is already an answer
        try:
            answer = Answer.objects.filter(question_id=question.pk, assessment_id=assessment.pk).latest("created")
            # Create an empty answer and save it, NOTE: not really necessary, but afraid of possible unexpected behaviour if removed
        except (KeyError, Answer.DoesNotExist):
            answer = Answer(assessment_id=assessment, question_id=question, user=request.user, status=Answer.Status.UA)
            answer.save()

        if question_id == 11:
            context["law_clusters"] = LawCluster.objects.all()

        # Add necessary context for questions that are not in phase 4
        context["answer"] = answer
        context["collab_list"] = Collaborator.objects.filter(answers=answer)
        context["collab_options"] = get_collab_options(assessment, answer)
        context["question_history"] = get_answers_sorted(assessment, question)

        return render(request, "base/q_detail.html", context)

# Save an answer to the database and alter it's completion status
@login_required
def save_answer(request, assessment_id, question_id):    

    if request.method == "POST":
        # Retrieve answer and assessment from the database
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
            question = Question.objects.get(pk=question_id)
            answer = Answer.objects.filter(assessment_id=assessment, question_id=question).latest("created")

        except (KeyError, Answer.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Opgeslagen antwoord is niet gevonden in de db!"})
        
        except (KeyError, Assessment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assessment kan niet gevond worden!"})

        except (KeyError, Question.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Vraag kan niet gevond worden!"})

        # Check if user is autorised
        if not user_has_edit_privilidge(request.user.pk, assessment):
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})
        
        # Put the POST request data into form
        answer_form = AnswerForm(request.POST)

        # Make sure the data is valid
        if answer_form.is_valid():

            # Only create a new answer if the answers content has been updated
            if answer_form.data["answer_content"].strip() != answer.answer_content:
                answer = Answer(assessment_id=assessment, user=request.user, question_id=question)

                # Update answer data
                answer.answer_content = answer_form.data["answer_content"].strip()# is_valid drops answer content from cleaned data?????
            
            #TODO: implement error for definitively saving empty answer:

            # Check the state of the question

            # Unanswered
            if answer_form.data["answer_content"].strip() == "":# is_valid drops answer content from cleaned data?????
                answer.status = Answer.Status.UA

            # Reviewed
            elif "reviewed" in request.POST:
                answer.status = Answer.Status.RV

            # Answered
            else:
                answer.status = Answer.Status.AW

            answer.save()

            # Only reverse the stored completion status when the return value indicates a change in completion
            assessment.complete_status = all_answers_reviewed(assessment)
            assessment.save()
                 
            # Return to question detail page with updated answer
            return HttpResponseRedirect(reverse("base:question_detail", args=(assessment_id, question_id,)))

        # Error
        else:
            return render(request, "errors/error.html", {"message": "Voer valide data in!"})
    else:
        return render(request, "errors/error.html", {"message": "Alleen POST request toegestaan!"})

# Add an existing collaborator to a question
@login_required
def add_collab(request, answer_id, collab_id):
    # Get the answer, assessment and collaborator
    try:
        answer = Answer.objects.get(pk=answer_id)
        collab = Collaborator.objects.get(pk=collab_id)
        assessment = Assessment.objects.get(pk=answer.assessment_id.id)

    except (KeyError, Answer.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker aan toe te voegen kan niet in database gevonden worden!"})
    
    except (KeyError, Collaborator.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker aan toe te voegen kan niet in database gevonden worden!"})
    
    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment kan niet gevond worden!"})

    # Check if user is autorised
    if not user_has_edit_privilidge(request.user.pk, assessment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})

    # Add it to the many-to-many relation
    answer.collaborator_set.add(collab)
    next = request.GET.get("next", reverse('base:question_detail', args=(answer.assessment_id.id, answer.question_id.id,)))

    return HttpResponseRedirect(next)

# Create a collaborator and add it to the current question
@login_required
def create_add_collab(request, answer_id):
    if request.method == "POST":
        # Get the answer and assessment
        try:
            answer = Answer.objects.get(pk=answer_id)
            assessment = Assessment.objects.get(pk=answer.assessment_id.id)

        except (KeyError, Answer.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Kan vraag om medewerker aan toe te voegen niet vinden in de database!"})

        except (KeyError, Assessment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assessment kan niet gevond worden!"})

        # Check if user is autorised
        if not user_has_edit_privilidge(request.user.pk, assessment):
            return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})
        
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
        assessment = Assessment.objects.get(pk=answer.assessment_id.id)

    except (KeyError, Answer.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Vraag om medewerker van te verwijderen bestaat niet in de database!"})

    except (KeyError, Collaborator.DoesNotExist) :
        return render(request, "errors/error.html", {"message": "Medewerker om van de vraag te verwijderen bestaat niet in de database!"})

    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment kan niet gevond worden!"})

    # Check if user is autorised
    if not user_has_edit_privilidge(request.user.pk, assessment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})

    else:
        # Delete relation and go back to next page
        answer.collaborator_set.remove(collab)

        # Check if there is any answer associated with the collaborator
        if not collab.answers.exists():
            collab.delete()# No answers associated, delete the collaborator

        return HttpResponseRedirect(request.GET.get("next", "/"))

@login_required
def info(request):
    assessments_list = Assessment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
    return render(request, "base/info.html" ,{"assessments_list": assessments_list}) 

@login_required
def add_editor(request, assessment_id, editor_id):
    try:
        assessment = Assessment.objects.get(pk=assessment_id)
    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment bestaat niet!"})
    
    if user_has_edit_privilidge(request.user.pk, assessment):
        editor = User.objects.get(pk=editor_id)
        assessment.user_group.add(editor)

        # TODO make it so that the page where the user came from is remembered and that the user returns to it
        return HttpResponseRedirect(reverse("base:detail", args=(assessment.id,)))
    
    else:
        return render(request, "errors/error.html", {"message": "Alleen de maker van een assessment kan editors toevoegen!"})

# Add an editor with editing priviledges to an assessment
@login_required 
def search_editor(request, assessment_id):
    # Find the assessment
    try:
        assessment = Assessment.objects.get(pk=assessment_id)
    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment bestaat niet!"})

    if user_has_edit_privilidge(request.user.id, assessment):

        # Get request shows only the search_page with an form to search for users by id
        if request.method == "GET":
            next = request.GET.get("next", reverse("base:detail", args=(assessment.id,)))
            return render(request, "base/search_editor.html", {"assessment": assessment, "next": next})

        """
        This version of adding editors to an assessment is for prototyping only in a controlled environment.
        When creating a more complete software solution, an inbox system should be put into place as to
        prevent people from spam adding them to projects.
        Also the adding of editors now goes by id, which may be subject to change but it will do for the purposes of this prototype.
        """

        # Post request contains the user id and reverts the user to a confirmation screen on wether they really want to add that user
        if request.method == "POST":
            form = SearchEditorForm(request.POST) 
            next = request.POST.get("next", reverse("base:detail", args=(assessment.id,)))

            # First check wether the given value is an integer
            if form.is_valid():

                # Make sure the editor added isn't the same user as the user sending the request
                if request.user.pk == form.cleaned_data["editor_id"]:
                    return render(request, "base/search_editor.html", {"assessment": assessment, "next": next, "error": "Kan jezelf niet als editor toevoegen!"})

                # Find an editor
                try:
                    editor = User.objects.get(pk=form.cleaned_data["editor_id"]) 

                # No user found with entered id
                except (KeyError, User.DoesNotExist):
                    return render(request, "base/search_editor.html", {"assessment": assessment, "next": next ,"error": "Kan geen editor vinden met dit id!"})

                # User found
                return render(request, "base/confirm_editor.html", {"assessment": assessment, "next": next, "editor": editor})
            
            # No integer entered
            else:
                return render(request, "base/search_editor.html", {"assessment": assessment, "next": next, "error": "Ingevoerde waarde moet een heel nummer zijn!"})
                
@login_required
def delete_editor(request, assessment_id, editor_id):
    # Find the assessment
    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        editor = User.objects.get(pk=editor_id)

    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment bestaat niet!"})
    
    except (KeyError, User.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Editor bestaat niet!"})

    # Check user privilidges
    if user_has_edit_privilidge(request.user.pk, assessment):
        
        # Delete the editor from the assessment en return to detail page
        assessment.user_group.remove(editor)
        return HttpResponseRedirect(reverse("base:detail", args=(assessment.id,)))
    
    else:
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen permissie om editors te verwijderen!"})

@login_required
def landing_page(request):
    assessments_list = Assessment.objects.filter(user__pk=request.user.pk).order_by("-date_last_saved")
    return render(request, "base/landing_page.html", {"assessments_list": assessments_list})
