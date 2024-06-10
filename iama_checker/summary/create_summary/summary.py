import pdfkit
from jinja2 import Environment, FileSystemLoader

from base.models import Question, Answer, Law, Phase4Answer

# Crude solution but gets the job done
def get_questions_by_phase(assesment):
    # Get the questions of phase 1-3 and their answers in a dict ordered by phase
    questions_by_phase = {}
    total_phasess = 3

    # Go through each phase
    for phase in range(total_phasess):
        # Create a list of dicts containing the question and answer info
        question_list = []
        questions = Question.objects.filter(question_phase=phase).exclude(question_number=0).order_by("question_number")
        if questions.exists():
            for question in questions:
                # Get the latest answer to dispaly or no answer at all
                try:
                    answer = Answer.objects.filter(question=question, assesment=assesment).latest("created")
                except (KeyError, Answer.DoesNotExist):
                    answer = "- Geen antwoord beschikbaar"

                # Construct the object to be displayed
                question_dict = {
                    "question_phase": question.question_phase,
                    "question_number": question.question_number,
                    "question_text": question.question_text,
                    "question_answer": answer
                }
                # Add the dict to the list of all the questions in this phase
                question_list.append(question_dict)
            # Add the list to the dictionary ordering them by phase
            questions_by_phase[str(phase)] = question_list
    return questions_by_phase

def get_laws(assesment):
    # Get the necessary objects from the db
    questions = Question.objects.filter(question_phase=5)# Remember that phase_number 5 contains the questions of phase4 in the original IAMA document
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
                phase4_object["answer"] = Phase4Answer.objects.filter(assesment=assesment, law=law, question=question).latest("created")
            except (KeyError, Phase4Answer.DoesNotExist):
                phase4_object["answer"] = "- Geen antwoord beschikbaar"

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
    }

    print(context)

def print_name_in_console():
    print(__name__)



if __name__ == "__main__":
    
    question_list_example = [
        {
            "question_phase": 1,
            "question_number": 1,
            "question_text": "Dit is de eerste vraag",
            "question_answer": "Dit is het antwoord op de eerste vraag"
        },
        {
            "question_phase": 2,
            "question_number": 2,
            "question_text": "Dit is de tweede vraag",
            "question_answer": "Dit is het antwoord op de tweede vraag"
        },
        {
            "question_phase": 3,
            "question_number": 3,
            "question_text": "Dit is de derde vraag",
            "question_answer": "Dit is het antwoord op de derde vraag"
        }
    ]

# Get the data to insert into the template
    rights_list_example = [
        {
            "name": "Grondrecht1",
            "phase4": [
                {
                    "question": "Eerste vraag stappenplan",
                    "answer": "Eerste antwoord"
                },
                {
                    "question": "Tweede vraag stappenplan",
                    "answer": "Tweede antwoord"
                }
            ]
        },
        {
            "name": "Grondrecht2",
            "phase4": [
                {
                    "question": "Eerste vraag stappenplan",
                    "answer": "Eerste antwoord"
                },
                {
                    "question": "Tweede vraag stappenplan",
                    "answer": "Tweede antwoord"
                }
            ]
        }
    ]

# Create the template
    env = Environment(loader=FileSystemLoader("templates/"))
    template = env.get_template("summary.html")
    context = {
        "assessment_name": "test_assessment",
        "question_list": question_list_example,
        "ultimately_responsible": {
            "person": "Joost Klein",
            "organisation": "Joost incorporated"
        },
        "rights": rights_list_example,
    }

# Fill in the template and output the content into the .html file to be converted to .pdf
    template_output = template.render(context)

    with open("input.html", 'w') as file:
        file.write(template_output)

    pdfkit.from_file("input.html", "output.pdf", css="static/style.css", options={"enable-local-file-access": ""})
