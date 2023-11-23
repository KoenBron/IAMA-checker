from django.db import models

# Create your models here.
class Assesment(models.Model):
    name = models.CharField(max_length=40)# Name of the assesment
    organisation = models.CharField(max_length=50)# Name of the organisation performing the assesment
    complete_status = models.BooleanField(default=False)
    date_last_saved = models.DateField(auto_now=True)