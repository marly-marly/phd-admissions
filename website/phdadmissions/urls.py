from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView, SupervisionView, CommentView, ApplicationSearchView, \
    ApplicationChoicesView, StatisticsView, SupervisorView, ApplicationFieldsView
from phdadmissions.views.documentations import FileView, DownloadView, ZipFileView, CsvFileView

urlpatterns = patterns(
    '',
    # Applications
    url(r'^application/$', ApplicationView.as_view()),
    url(r'^supervision/$', SupervisionView.as_view()),
    url(r'^comment/$', CommentView.as_view()),
    url(r'^search/$', ApplicationSearchView.as_view()),
    url(r'^newFilesIndex/application/$', ApplicationChoicesView.as_view()),
    url(r'^statistics/$', StatisticsView.as_view()),
    url(r'^supervisor/$', SupervisorView.as_view()),
    url(r'^file/$', FileView.as_view()),
    url(r'^download/$', DownloadView.as_view()),
    url(r'^zip_download/$', ZipFileView.as_view()),
    url(r'^application_fields/$', ApplicationFieldsView.as_view()),
    url(r'^csv_download/$', CsvFileView.as_view()),

)
