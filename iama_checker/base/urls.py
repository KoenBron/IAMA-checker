from django.urls import path

from . import views

app_name = "base"

urlpatterns = [
    path("", views.greeting, name="greeting"),
    path("bink_test/", views.bink_test, name="bink_test"),
]