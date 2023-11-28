from django.forms import ModelForm, TextInput
from .models import Assesment

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