from logging import log
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from base.base_view_helper import user_has_edit_privilidge
from base.models import Assesment

from .create_summary import summary

@login_required
def create_summary(request, assesment_id):
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment om een overzicht van te maken bestaat niet!"})

    if not user_has_edit_privilidge(request.user.id, assesment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})

    next = request.GET.get("next", reverse("base:detail", args=(assesment.id,)))
    if summary.produce_summary(assesment):
        return HttpResponseRedirect(next)

    else:
        return render(request, "errors/error.html", {"message": "Er is iets fout gegaan bij het printen!"})

    

    

