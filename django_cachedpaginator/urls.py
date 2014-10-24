from django.conf.urls import patterns, url
from .views import TestView


urlpatterns = patterns(
    '',
    url(r'^', TestView.as_view()),
)
