from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView

urlpatterns = patterns(
    '',

    # Applications
    url(r'^application/$', ApplicationView.as_view()),
)
