import io
from logging import log
from django.shortcuts import render, reverse
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from base.base_view_helper import user_has_edit_privilidge
from base.models import Assesment

from .create_summary import summary

@login_required
def create_summary(request, assesment_id):
    # Make sure the assesment exists and the request user has access
    try:
        assesment = Assesment.objects.get(pk=assesment_id)
    except (KeyError, Assesment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assesment om een overzicht van te maken bestaat niet!"})

    if not user_has_edit_privilidge(request.user.id, assesment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})

    # Create the pdf
    pdf = summary.produce_summary(assesment)
    print(type(pdf))
    buffer = io.BytesIO()
    buffer.write(pdf)
    buffer.seek(0)

    # return render(request, "summary/download.html", {"assesment": assesment})
    return FileResponse(buffer, as_attachment=True, filename="{0}_IAMA_overzicht.pdf".format(assesment.name))


# @login_required
# def download_summary(request, assesment_id):
#     # Make sure the assesment exists and the request user has access
#     try:
#         assesment = Assesment.objects.get(pk=assesment_id)
#     except (KeyError, Assesment.DoesNotExist):
#         return render(request, "errors/error.html", {"message": "Assesment om een overzicht van te maken bestaat niet!"})
#
#     if not user_has_edit_privilidge(request.user.id, assesment):
#         return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})
#     
#     try:
#         with open("summary_output/output_{0}.pdf".format(assesment.pk), "br") as file:
#             return FileResponse(file, as_attachment=True, filename="{%}_IAMA_overzicht.pdf".format(assesment.name))
#     except FileNotFoundError:
#         return render(request, "summary/download.html", {"assesment": assesment, "error": "Er ging iets mis met het downloaden van de file. Probeer het later nog eens!"})


    

    

