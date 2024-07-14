# IAMA-checker

IAMA Checker is a Dutch web-based software application prototype that is meant to show how software tooling can aid and guide its users in performing a IAMA assessment. The prototype is made with Django 5.0.4 using its templating system as a static front-end and includes only phases 1 & 4 of the original IAMA document.
IAMA Checker boasts a number of features to assist its users and expand on the functionalities of IAMA, these are:

- User collaboration on assessments
- Assessment and answer status tracking
- Generating PDF summary of assessments
- Providing additional context and context to questions

## Installation

First make sure you have Python 3.10 installed and then clone this repository, afterwards install the dependencies in requirements.txt.

    $ pip install -r requirements.txt

Navigate to the `iama_checker/` directory and make sure to create the database tables.

    $ python3 manage.py makemigrations
    $ python3 manage.py migrate

The question, lawcluster (appendix to phase 4) and reference content is stored as django fixtures in a json format (stored in `iama_checker/base/fixtures/`). Load this content into the database first with:

    $ python3 manage.py loaddata questions lawclusters references

Now you can run the application on localhost.

    $ python3 manage.py runserver

## Security Disclaimer

IAMA Checker is a proof-of-concept, meaning that security and deployment were not the focus of development. To this end the security key in settings.py is included in the git and the password validators are used. Furthermore, the default session handling and authentication of Django is used. The static files (CSS, JavaScript files) are served in development mode and thus grossly inefficient and insecurely done.

## PDF summary

The summary is generated using the data from the assessment. The template is an HTML file that is filled through using Jinja2, this HTML file is then converted through Python PDFkit to a pdf file that is presented as a download option. This method was chosen so as to make styling the document as easy as possible. The implementation can be found in `iama_checker/summary/`.

## Assessment questions and phases

To create new questions and/or phases you need to include new entries in the fixtures files stored in `iama_checker/base/fixtures/`, the phase introduction pages all have `question_number = 0`. Questions/phases objects have the following fields:

- question_title
- question_text (the question as posed in the original IAMA)
- question_context (additional and optional extra context)
- question_instruction (short text explaining what is required in an answer, not necessary in phase introductions)
- question_phase (number of the phase)
- question_number (number of the question in the phase, 0 means the object is a phase introduction page)

## front-end
The front-end is based on the Django material-dashboard template by [creative-tim](https://www.creative-tim.com/product/material-dashboard-django) and further developed using [Bootstrap 5.3](https://getbootstrap.com/docs/5.3/getting-started/introduction/).

## How to contribute

The 3 main points for improvements of this proof-of-concept are the following:

- Incorporate JavaScript to make the the user collaboration on assessments dynamic instead of static, for example: real time collaboration like google docs and the ability to highlight parts of text with comments.
- Make the user interface less ambiguous, so users always know what parts are interactable and if they are already experienced with the application, how they can move about quickly through the appliction.
- Incorporated icons and other toggleable buttons to declutter the question and phase pages, thus making all the additional context and explanation optional to read.
- Expand on the testing for views and other features.


## Testing

There are a number of tests included in the `base` application for the testing of the views, though not some of these are outdated and will probably give false negatives.
