from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("create_assessment", views.create_assessment, name="create_assessment"),
    path("delete_assessment/<int:assessment_id>", views.delete_assessment, name="delete_assessment"),
    path("update_assessment/<int:assessment_id>", views.update_assessment, name="update_assessment"),
    path("assessments/<int:assessment_id>", views.detail, name="detail"),
    path("assessments/<int:assessment_id>/question/<int:question_id>", views.question_detail, name="question_detail"),
    path("assessments/<int:assessment_id>/question/<int:question_id>/save_answer", views.save_answer, name="save_answer"),
    path("create_add_collab/<int:answer_id>", views.create_add_collab, name="create_add_collab"),
    path("add_collab/<int:answer_id>/<int:collab_id>", views.add_collab, name="add_collab"),
    path("delete_collab/<int:answer_id>/<int:collab_id>", views.delete_collab, name="delete_collab"),
    path("home", views.home, name="home"),
    path("", views.landing_page, name="landing_page"),
    path("info", views.info, name="info"),
    path("add_editor/<int:assessment_id>/<int:editor_id>", views.add_editor, name="add_editor"),
    path("search_editor/<int:assessment_id>", views.search_editor, name="search_editor"),
    path("delete_editor/<int:assessment_id>/<int:editor_id>", views.delete_editor, name="delete_editor"),
]
