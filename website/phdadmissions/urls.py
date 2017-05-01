from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView, SupervisionView, CommentView, ApplicationSearchView, \
    ApplicationChoicesView

urlpatterns = patterns(
    '',
    # Applications
    url(r'^application/$', ApplicationView.as_view()),
    url(r'^supervision/$', SupervisionView.as_view()),
    url(r'^comment/$', CommentView.as_view()),
    url(r'^search/$', ApplicationSearchView.as_view()),
    url(r'^choices/application/$', ApplicationChoicesView.as_view()),
)
