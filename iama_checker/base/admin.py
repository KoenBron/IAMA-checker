from django.contrib import admin
from .models import Assesment, Question, Answer
# Register your models here.

admin.site.register(Assesment)
admin.site.register(Answer)
admin.site.register(Question)