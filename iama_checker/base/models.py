from django.db import models
from django.contrib.auth.models import User

# Helper functions to set be able to set User object as a foreignkey
def user_sentinel():
    return User.objects.get_or_create(username="Default_user", password="Default_password")[0]

def user_pk_sentinel():
    return user_sentinel().pk

# Create your models here.
class Assesment(models.Model):
    name = models.CharField(max_length=40)# Name of the assesment
    organisation = models.CharField(max_length=50)# Name of the organisation performing the assesment
    complete_status = models.BooleanField(default=False)
    date_last_saved = models.DateField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=user_pk_sentinel)