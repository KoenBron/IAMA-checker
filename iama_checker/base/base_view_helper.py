# File with the helpler functions for the base views
from .models import Assesment, Question, Answer

# Check if the logged in user is the authorised to edit and view the assesment_is 
# Return True if authorised, else False
def user_has_edit_privilidge(user_id, assesment):
    # Check if authorised
    return (assesment.user.id == user_id) or (assesment.user_group.filter(id = user_id).exists())

# Return true if all answers have the reviewed status
def all_answers_reviewed(assesment_id):
    # Loop through all the answers of an assesment 
    answers = Answer.objects.filter(assesment_id=assesment_id)
    for answer in answers:
        # Found an answer that isn't reviewed
        if answer.status != Answer.Status.RV:
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

# Retrieve a list of options to add as possible collaborators to an answer
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
    # NOTE: color can be removed
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

