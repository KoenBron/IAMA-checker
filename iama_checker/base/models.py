from django.db import models
from django.contrib.auth.models import User

# Helper functions to set be able to set User object as a foreignkey
def user_sentinel():
    return User.objects.get_or_create(username="Default_user", password="Default_password")[0]

def user_pk_sentinel():
    return user_sentinel().pk

def reference_sentinel():
    return Reference.objects.get_or_create(description="Example description of reference", url="www.example.com")

# Create your models here.
class Assesment(models.Model):
    name = models.CharField(max_length=40)# Name of the assesment
    organisation = models.CharField(max_length=50)# Name of the organisation performing the assesment
    complete_status = models.BooleanField(default=False)# Complete when all questions have been answered
    date_last_saved = models.DateField(auto_now=True)# Automatically saves new value when this object is saved
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=user_pk_sentinel)

class Question(models.Model):
    question_title = models.CharField(max_length=140, default="Question title")
    question_text = models.TextField()# Content to display
    question_phase = models.IntegerField() # Phase number of the question
    question_number = models.IntegerField() # Question number in the phase

class Answer(models.Model):
    class Status(models.TextChoices):
        RV = "RV", "reviewed"
        AW = "AW", "answered"
        UA = "UA", "unanswered"
    
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.UA)# Whether it's correctly filled in or not
    answer_content = models.TextField(default="") # Content of the answer

    # Attributes to identify the corresponding answer
    assesment_id = models.ForeignKey(Assesment, on_delete=models.CASCADE, default=0)# Related assesment
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE, default=0) # Related question
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=user_pk_sentinel)# User that answers

# Could also have a relation to Assesment, but would be redundant info since the answer is already related
# Don't know what is best practice here, so could be revisited later.
class Collaborator(models.Model):
    name = models.CharField(max_length=40)
    organisation = models.CharField(max_length=60)
    # Many to many field as answer can have multiply collaborators and vice versa
    answers = models.ManyToManyField(Answer)

class Reference(models.Model):
    title = models.CharField(max_length=64, default="Example title")
    description = models.TextField()
    url = models.URLField(max_length=128)
    questions = models.ManyToManyField(Question)