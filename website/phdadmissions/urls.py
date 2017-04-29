from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView, SupervisionView

urlpatterns = patterns(
    '',

    # Applications
    url(r'^application/$', ApplicationView.as_view()),
    url(r'^supervision/$', SupervisionView.as_view()),
)
