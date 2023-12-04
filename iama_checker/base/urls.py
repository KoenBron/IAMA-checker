from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("bink_test/", views.bink_test, name="bink_test"),
    path("create_assesment/", views.create_assesment, name="create_assesment"),
    path("update_assesment/<int:assesment_id>", views.update_assesment, name="update_assesment"),
    path("assesments/<int:assesment_id>/", views.detail, name="detail"),
    path("", views.home, name="home")
]