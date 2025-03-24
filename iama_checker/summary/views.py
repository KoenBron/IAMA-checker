import io
from logging import log
from django.shortcuts import render, reverse
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from base.base_view_helper import user_has_edit_privilidge
from base.models import Assessment

from .create_summary import summary

@login_required
def create_summary(request, assessment_id):
    # Make sure the assessment exists and the request user has access
    try:
        assessment = Assessment.objects.get(pk=assessment_id)
    except (KeyError, Assessment.DoesNotExist):
        return render(request, "errors/error.html", {"message": "Assessment om een overzicht van te maken bestaat niet!"})

    if not user_has_edit_privilidge(request.user.id, assessment):
        return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})

    # Create the pdf
    pdf = summary.produce_summary(assessment)
    buffer = io.BytesIO()
    buffer.write(pdf)
    buffer.seek(0)

    # return render(request, "summary/download.html", {"assessment": assessment})
    return FileResponse(buffer, as_attachment=True, filename="{0}_IAMA_overzicht.pdf".format(assessment.name))


# @login_required
# def download_summary(request, assessment_id):
#     # Make sure the assessment exists and the request user has access
#     try:
#         assessment = Assessment.objects.get(pk=assessment_id)
#     except (KeyError, Assessment.DoesNotExist):
#         return render(request, "errors/error.html", {"message": "Assessment om een overzicht van te maken bestaat niet!"})
#
#     if not user_has_edit_privilidge(request.user.id, assessment):
#         return render(request, "errors/error.html", {"message": "Gebruiker heeft geen toegang tot deze assessment!"})
#     
#     try:
#         with open("summary_output/output_{0}.pdf".format(assessment.pk), "br") as file:
#             return FileResponse(file, as_attachment=True, filename="{%}_IAMA_overzicht.pdf".format(assessment.name))
#     except FileNotFoundError:
#         return render(request, "summary/download.html", {"assessment": assessment, "error": "Er ging iets mis met het downloaden van de file. Probeer het later nog eens!"})


    

    

