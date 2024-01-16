from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import AssesmentForm, AnswerForm, CollaboratorForm
from .models import Assesment, Question, Answer, Collaborator, Reference
from django.http import HttpResponseRedirect 
from django.urls import reverse

# Return true if all answers have the reviewed status
def all_answers_reviewed(assesment_id):
    # Loop through all the answers of an assesment 
    answers = Answer.objects.filter(assesment_id=assesment_id)
    for answer in answers:
        # Found an answer that isn't reviewed
        if answer.status != Answer.Status.RV:
            print(answer.status)
            return False
    return True
# Generates a list of dictionaries for all jobs required in a phase
def jobs_per_phase(phase_num):
    questions = Question.objects.filter(question_phase=phase_num)
    jobs = []
    for question in questions:
        if question.question_number != 0:
            job = {
                "q_number": question.question_number,
                "job_list": question.jobs_as_py_list(),
            }
            jobs.append(job)
    return jobs


# Generates emtpy answers for all of questions in the assesment
def generate_empty_answers(assesment, user):
    # Go through all the questions
    for question in Question.objects.all():
        # Only create answers for question and not phase introductions 
        if question.question_number != 0:
            # Create an empty answer and store it in the db
            answer = Answer(assesment_id=assesment, question_id=question, user=user, status=Answer.Status.UA)
            answer.save()

# Retrieve a list of options to add as possible collaobrators to an answer
def get_collab_options(assesment, curr_answer):
    return_collab = []
    # Get all the answers associated with the assesment
    answers = Answer.objects.filter(assesment_id=assesment.pk)

    # Get all the collaborators
    for answer in answers:
        # List comprehension to add only collabs not already present in the answer
        options = answer.collaborator_set.all()
        exclude = curr_answer.collaborator_set.all()
        to_extend = [option for option in options if option not in exclude]

        return_collab.extend(to_extend)

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

            # Have the html stored in a string-variable to reduce html clutter in the question_index.html file
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
            assesment = Assesment(name=form.cleaned_data['name'].strip(), organisation=form.cleaned_data['organisation'].strip(), user=request.user)
            assesment.save()
            
            # Create empty answers to ensure correct and predictable behaviour
            generate_empty_answers(assesment, request.user)
            
            # Go to the detail page of the new assignment
            return HttpResponseRedirect(reverse("base:detail", args=(assesment.id,)))
    
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
            assesment = Assesment.objects.filter(user__pk=request.user.pk, id=assesment_id)[0]
        except (KeyError, Assesment.DoesNotExist):
            return render(request, "errors/error.html", {"message": "Assesment om te updaten bestaat niet!"})

        # Verify the users autority to perform this action
        if request.user.pk == assesment.user.pk:
            return render(request, "errors/error.html", {"message": "Gebruiker is niet toegestaan om deze assesment te updaten!"})    

        # Create a form to easily validate and extract the data
        form = AssesmentForm(request.POST)
        if form.is_valid():
            # We don't use the update() method so the assesment.date_last_saved value is newly set
            assesment.name = form.cleaned_data['name'].strip()
            assesment.organisation = form.cleaned_data['organisation'].strip()
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
            collab = Collaborator(name=form.cleaned_data["name"].strip(), organisation=form.cleaned_data["organisation"].strip())
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















