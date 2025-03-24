from django.contrib import admin
from .models import Assessment, Question, Answer
# Register your models here.

admin.site.register(Assessment)
admin.site.register(Answer)
admin.site.register(Question)