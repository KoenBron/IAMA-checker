import pdfkit
from jinja2 import Environment, FileSystemLoader

# from ...base.models import Question, Answer
#
# def get_template_context(assesment):
#     # Get the questions of phase 1-3 and their answers in a dict ordered by phase
#     questions = Question.objects.filter(question_phase__lte=3).exclude(question_number=0)
#     question_by_phase = []
#     for question in questions:
#         answer = Answer.objects.filter(question=question, assesment=assesment).latest("created")
#         question_dict = {
#             "question_phase": question.question_phase,
#             "question_number": question.question_number,
#             "question_text": question.question_text,
#             "question_answer": "" 
#         }
#
#
# def produce_summary(assesment):
#     # Get context objects for the template
#     context = get_template_context(assesment)



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
        "utlimately_responsible": {
            "person": "Joost Klein",
            "organisation": "Joost inc."
        },
        "rights": rights_list_example,
    }

# Fill in the template and output the content into the .html file to be converted to .pdf
    template_output = template.render(context)

    with open("input.html", 'w') as file:
        file.write(template_output)

    pdfkit.from_file("input.html", "output.pdf", css="static/style.css", options={"enable-local-file-access": ""})
