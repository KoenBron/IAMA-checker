from django.forms import Form, IntegerField, ModelForm, TextInput, Textarea, BooleanField
from .models import Assessment, Collaborator

# The form to create or alter an assessment as a user
class AssessmentForm(ModelForm):
    class Meta:
        model = Assessment
        fields = ["name", "organisation", "ultimately_responsible"]
        widgets = {
            "name": TextInput(attrs={
                "class": "form-control",
            }),
            "organisation": TextInput(attrs={
                "class": "form-control",
            }),
            "ultimately_responsible": TextInput(attrs={
                "class": "form-control",
            })
        }

# The form to handle input validation for Answer model
class AnswerForm(Form):
    # Review button can be submitted checked or unchecked
    reviewed = BooleanField(required=False)
    cut_off = BooleanField(required=False)
    answer_content = Textarea()

# For handling create collaborator post request
class CollaboratorForm(ModelForm):
    class Meta:
        model = Collaborator
        fields = ["name", "discipline", "organisation"]

# For recieving the user id of a potential editor
class SearchEditorForm(Form):
    editor_id = IntegerField(required=True)
