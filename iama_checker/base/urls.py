from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("create_assesment/", views.create_assesment, name="create_assesment"),
    path("update_assesment/<int:assesment_id>", views.update_assesment, name="update_assesment"),
    path("assesments/<int:assesment_id>/", views.detail, name="detail"),
    path("assesments/<int:assesment_id>/question/<int:question_id>", views.question_detail, name="question_detail"),
    path("assesments/<int:assesment_id>/question/<int:question_id>/save_answer", views.save_answer, name="save_answer"),
    path("", views.home, name="home")
]