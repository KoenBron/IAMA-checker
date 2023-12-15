from django.forms import Form, ModelForm, TextInput, Textarea, BooleanField
from .models import Assesment, Answer

# The form to create or alter an assesment as a user
class AssesmentForm(ModelForm):
    class Meta:
        model = Assesment
        fields = ["name", "organisation"]
        widgets = {
            "name": TextInput(attrs={
                "class": "form-control",
            }),
            "organisation": TextInput(attrs={
                "class": "form-control",
            })
        }

# The form to handle input validation for Answer model
class AnswerForm(Form):
    # Review button can be submitted checked or unchecked
    reviewed = BooleanField(required=False)
    answer_content = Textarea()