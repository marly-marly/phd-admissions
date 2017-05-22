from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView, SupervisionView, CommentView, ApplicationSearchView, \
    ApplicationChoicesView, StatisticsView, SupervisorView, FileView, DownloadView

urlpatterns = patterns(
    '',
    # Applications
    url(r'^application/$', ApplicationView.as_view()),
    url(r'^supervision/$', SupervisionView.as_view()),
    url(r'^comment/$', CommentView.as_view()),
    url(r'^search/$', ApplicationSearchView.as_view()),
    url(r'^multiFileIndex/application/$', ApplicationChoicesView.as_view()),
    url(r'^statistics/$', StatisticsView.as_view()),
    url(r'^supervisor/$', SupervisorView.as_view()),
    url(r'^file/$', FileView.as_view()),
    url(r'^download/$', DownloadView.as_view()),

)
