from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = "secure"
urlpatterns = [
    #path(...)
    path("", views.index, name="index"),
]