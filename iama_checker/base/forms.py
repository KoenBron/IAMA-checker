from django.forms import ModelForm
from .models import Assesment

# The form to create or alter an assesment as a user
class AssesmentForm(ModelForm):
    class Meta:
        model = Assesment
        fields = ["name", "organisation"]