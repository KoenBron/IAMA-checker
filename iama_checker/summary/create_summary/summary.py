import pdfkit
from jinja2 import Template, Environment, FileSystemLoader

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

# Load the template to substitue data on
env = Environment(loader=FileSystemLoader("templates/"))
template = env.get_template("summary.html")

# Get the data to insert into the template
context = {
    "assessment_name": "test_assessemnt",
    "question_list": question_list_example,
    "utlimately_responsible": {
        "person": "Joost Klein",
        "organisation": "Joost inc."
    },
}

# Fill in the template and output the content into the .html file to be converted to .pdf
template_output = template.render(context)

with open("input.html", 'w') as file:
    file.write(template_output)

pdfkit.from_file("input.html", "output.pdf", css="static/style.css", options={"enable-local-file-access": ""})
