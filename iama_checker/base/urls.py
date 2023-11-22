from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("bink_test/", views.bink_test, name="bink_test"),
]