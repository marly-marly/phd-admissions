from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView, SupervisionView, CommentView

urlpatterns = patterns(
    '',

    # Applications
    url(r'^application/$', ApplicationView.as_view()),
    url(r'^supervision/$', SupervisionView.as_view()),
    url(r'^comment/$', CommentView.as_view())
)
