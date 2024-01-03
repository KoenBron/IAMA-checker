from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("create_assesment/", views.create_assesment, name="create_assesment"),
    path("update_assesment/<int:assesment_id>", views.update_assesment, name="update_assesment"),
    path("assesments/<int:assesment_id>/", views.detail, name="detail"),
    path("assesments/<int:assesment_id>/question/<int:question_id>", views.question_detail, name="question_detail"),
    path("assesments/<int:assesment_id>/question/<int:question_id>/save_answer", views.save_answer, name="save_answer"),
    path("create_add_collab/<int:answer_id>", views.create_add_collab, name="create_add_collab"),
    path("add_collab/<int:answer_id>/<int:collab_id>", views.add_collab, name="add_collab"),
    path("delete_collab/<int:answer_id>/<int:collab_id>", views.delete_collab, name="delete_collab"),
    path("", views.home, name="home"),
]