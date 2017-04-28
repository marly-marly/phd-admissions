from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView

urlpatterns = patterns(
    '',

    # Applications
    url(r'^applications/add_or_edit/$', ApplicationView.as_view()),
)
