# File with the helpler functions for the base views
from .models import Assesment, Phase4Answer, Question, Answer, Law

def get_answers_sorted(assesment, question):
    return_list = Answer.objects.filter(assesment_id=assesment, question_id=question).order_by("-created")
    
    # Eliminate the answers with empty answer bodies
    return [answer for answer in return_list if answer.answer_content != ""]

# Check if the logged in user is the authorised to edit and view the assesment_is 
# Return True if authorised, else False
def user_has_edit_privilidge(user_id, assesment):
    # Check if authorised
    return (assesment.user.id == user_id) or (assesment.user_group.filter(id = user_id).exists())

# Return true if all answers have the reviewed status
def all_answers_reviewed(assesment_id):
    # Loop through all questions
    for question in Question.objects.exclude(question_phase=5):
        # Make sure to only check questions and not phase intros, then check only if the latest element is not reviewed
        if question.question_number != 0 and Answer.objects.filter(assesment_id=assesment_id, question_id=question).latest("created").status != Answer.Status.RV:
            return False

    # Check if laws are completed
    for law in Law.objects.filter(assesment_id=assesment_id):
        if law.status == Law.Status.ICP:
            return False
    # All answer have reviewed status
    return True


# Generates a list of dictionaries for all jobs required in a phase
def jobs_per_phase(phase_num):
    questions = Question.objects.filter(question_phase=phase_num)
    jobs = []
    for question in questions:
        if question.question_number != 0:
            job = {
                "q_number": question.question_number.normalize,
                "job_list": question.jobs_as_py_list(),
            }
            jobs.append(job)
    return jobs

# Generates emtpy answers for all of questions in the assesment
def generate_empty_answers(assesment, user):
    # Go through all the questions
    for question in Question.objects.exclude(question_phase=5):
        # Only create answers for question and not phase introductions 
        if question.question_number != 0:
            # Create an empty answer and store it in the db
            answer = Answer(assesment_id=assesment, question_id=question, user=user, status=Answer.Status.UA)
            answer.save()

# Generate empty answers for a law in phase phase 4
def generate_empty_law_answers(law):
    for question in Question.objects.filter(question_phase=5):
        if question.question_number != 0:
            answer = Phase4Answer(law=law, assesment_id=law.assesment, question_id=question, user=law.assesment.user, status=Answer.Status.UA) 
            answer.save()

# Retrieve a list of options to add as possible collaborators to an answer
def get_collab_options(assesment, curr_answer):
    return_collab = []
    # Get all the answers associated with the assesment
    answers = Answer.objects.filter(assesment_id=assesment.pk)
    exclude = curr_answer.collaborator_set.all()

    # Get all the collaborators
    for answer in answers:
        # List comprehension to add only collabs not already present in the answer and not already added to the list of potential collabs
        options = answer.collaborator_set.all()
        to_extend = [option for option in options if option not in exclude and option not in return_collab]

        return_collab.extend(to_extend)

    return return_collab

# Retrieves the completion status as html of every answer related to an assesment
# and puts them in a dictionary that is returned
def get_complete_status(request, assesment):
    question_list = Question.objects.exclude(question_phase=5)
    status_list = {}
    for question in question_list:
        try:
            # Match an answer based on question_id, user_id and assesment_id
            answer = Answer.objects.filter(question_id=question.pk, assesment_id=assesment.id).latest("created")
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

# Return the law complete or incomplete status based on wether the phase 4 questions of that law were reviewed
def is_law_complete(law):
    # Loop through all questions of phase 4, remember that the question are have 
    for question in Question.objects.filter(question_phase=5):
        # Make sure to only check questions and not phase intros, then check only if the latest element is not reviewed
        if question.question_number != 0 and Phase4Answer.objects.filter(law=law, assesment_id=law.assesment, question_id=question).latest("created").status != Answer.Status.RV:
            return Law.Status.ICP
    # All answer have reviewed status
    return Law.Status.CP

# Get the completion status of all the questions for a given law
def get_law_complete_status(request, assesment):
    questions = Question.objects.filter(question_phase=5)
    status_list = {}
    for question in questions:
        try:
            # Match an answer based on question_id, user_id and assesment_id
            answer = Phase4Answer.objects.filter(question_id=question, assesment_id=assesment).latest("created")

            # Have the html stored in a string-variable to reduce html clutter in the question_index.html file
            match answer.status:
                case Answer.Status.UA:
                    status_list[str(question.id)] = "<span class='badge badge-danger badge-pill'>Onbeantwoord</span>"
                
                case Answer.Status.AW:
                    status_list[str(question.id)] = "<span class='badge badge-warning badge-pill'>Beantwoord</span>"

                case Answer.Status.RV:
                    status_list[str(question.id)] = "<span class='badge badge-success badge-pill'>Reviewed</span>"

        # Answers are created when the related question_page is first visited so, missing object also means unanswered 
        except (KeyError, Answer.DoesNotExist):
            status_list[str(question.id)] = "<span class='badge badge-danger badge-pill'>Onbeantwoord</span>"

    return status_list
