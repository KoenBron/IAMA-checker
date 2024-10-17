import pdfkit
from jinja2 import Environment, FileSystemLoader

from base.models import Question, Answer, Law, Phase4Answer

# Crude solution but gets the job done
def get_questions_by_phase(assesment):
    # Get all 4 phases as dict and group them in the list
    questions_by_phase = []
    total_phases = 5

    # Go through each phase
    for phase in range(1,total_phases):
        # Create a list of dicts containing the question and answer info
        question_list = []
        questions = Question.objects.filter(question_phase=phase).exclude(question_number=0).order_by("question_number")
        if questions.exists():
            for question in questions:
                # Get the latest answer to display or no answer at all
                try:
                    answer = Answer.objects.filter(question_id=question, assesment_id=assesment).latest("created").answer_content
                except (KeyError, Answer.DoesNotExist):
                    answer = "- Geen antwoord beschikbaar"
                # Just in case something funky happened to the answer content
                if answer.strip() == "" : answer = "- Geen antwoord beschikbaar"


                # Construct the object to be displayed
                question_dict = {
                    "question_phase": question.question_phase,
                    "question_number": question.question_number,
                    "question_text": question.question_text,
                    "question_answer": answer
                }
                 
                # Add the dict to the list of all the questions in this phase
                question_list.append(question_dict)

            # Add the dict to the list of phases
            questions_by_phase.append({"phase": phase, "question_list": question_list})

    return questions_by_phase

def get_laws(assesment):
    # Get the necessary objects from the db
    questions = Question.objects.filter(question_phase=4)
    laws = Law.objects.filter(assesment=assesment)
    
    # Setup the list of dicts that represent all the law objects related to this assesment
    law_list = []
    
    # Go through each law and construct the law object
    for law in laws:
        law_object = {
            "name": law.name,
            "phase4": []
        }

        # Append all the answers and question of phase4
        for question in questions:
            phase4_object = {
                "question": question.question_text,
            }
            
            # Either get the associated answer or alternative message
            try:
                phase4_object["answer"] = Phase4Answer.objects.filter(assesment_id=assesment, law=law, question_id=question).latest("created").answer_content
            except (KeyError, Phase4Answer.DoesNotExist):
                phase4_object["answer"] = "- Geen antwoord beschikbaar"
            if phase4_object["answer"].strip() == "" : phase4_object["answer"] = "- Geen antwoord beschikbaar"

            # Append the question/answer dict to the phase4 object list
            law_object["phase4"].append(phase4_object)

        # Append the law object to the list of law objects
        law_list.append(law_object)

    return law_list


def produce_summary(assesment):
    # Get context objects for the template
    context = {
        "questions": get_questions_by_phase(assesment),
        "laws": get_laws(assesment),
        "assessment_name": assesment.name,
        "ultimately_responsible": {
            "person": assesment.ultimately_responsible,
            "organisation": assesment.organisation
        }
    }

    # Create the environment for jinja2 to load the template from the templates/ directory
    env = Environment(loader=FileSystemLoader("summary/create_summary/templates/"))
    template = env.get_template("summary.html")

    # Get the filled in template and write it to the input file
    template_output = template.render(context)
    with open("input.html", "w") as input:
        input.write(template_output)

    # Convert the filled in .html file to a .pdf file
    return pdfkit.from_file("input.html", css="summary/create_summary/static/style.css", options={"enable-local-file-access": ""})

def delete_summary(assesment):
    pass

