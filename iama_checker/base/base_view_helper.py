# File with the helpler functions for the base views
from .models import Assessment, Question, Answer

def get_answers_sorted(assessment, question):
    return_list = Answer.objects.filter(assessment_id=assessment, question_id=question).order_by("-created")
    
    # Eliminate the answers with empty answer bodies
    return [answer for answer in return_list if answer.answer_content != ""]

# Check if the logged in user is the authorised to edit and view the assessment_is 
# Return True if authorised, else False
def user_has_edit_privilidge(user_id, assessment):
    # Check if authorised
    return (assessment.user.id == user_id) or (assessment.user_group.filter(id = user_id).exists())

# Return true if all answers have the reviewed status
def all_answers_reviewed(assessment_id):
    # Loop through all questions
    for question in Question.objects.all():
        # Make sure to only check questions and not phase intros, then check only if the latest element is not reviewed
        if question.question_number != 0 and Answer.objects.filter(assessment_id=assessment_id, question_id=question).latest("created").status != Answer.Status.RV:
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

# Generates emtpy answers for all of questions in the assessment
def generate_empty_answers(assessment, user):
    # Go through all the questions
    for question in Question.objects.all():
        # Only create answers for question and not phase introductions 
        if question.question_number != 0:
            # Create an empty answer and store it in the db
            answer = Answer(assessment_id=assessment, question_id=question, user=user, status=Answer.Status.UA)
            answer.save()

# Retrieve a list of options to add as possible collaborators to an answer
def get_collab_options(assessment, curr_answer):
    return_collab = []
    # Get all the answers associated with the assessment
    answers = Answer.objects.filter(assessment_id=assessment.pk)
    exclude = curr_answer.collaborator_set.all()

    # Get all the collaborators
    for answer in answers:
        # List comprehension to add only collabs not already present in the answer and not already added to the list of potential collabs
        options = answer.collaborator_set.all()
        to_extend = [option for option in options if option not in exclude and option not in return_collab]

        return_collab.extend(to_extend)

    return return_collab

# Retrieves the completion status as html of every answer related to an assessment
# and puts them in a dictionary that is returned
def get_complete_status(request, assessment):
    question_list = Question.objects.all()
    status_list = {}
    for question in question_list:
        try:
            # Match an answer based on question_id, user_id and assessment_id
            answer = Answer.objects.filter(question_id=question.pk, assessment_id=assessment.id).latest("created")
            status = ""

            # Have the html stored in a string-variable to reduce html clutter in the question_index.html file
            match answer.status:
                case Answer.Status.UA:
                    status = "<span class='badge badge-danger badge-pill'>Nog beantwoorden</span>"
                
                case Answer.Status.AW:
                    status = "<span class='badge badge-warning badge-pill'>Concept</span>"

                case Answer.Status.RV:
                    status = "<span class='badge badge-success badge-pill'>Definitief</span>"
        # Answers are created when the related question_page is first visited so, missing object also means unanswered 
        except (KeyError, Answer.DoesNotExist):
            status = "<span class='badge badge-danger badge-pill'>Nog beantwoorden</span>"
        # Append dict
        status_list[str(question.id)] = status

    return status_list
