from django.conf.urls import url
from .views import json_frapp

urlpatterns = [
    url(r'^frapp/$', json_frapp),
]