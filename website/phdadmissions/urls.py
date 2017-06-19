from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView, SupervisionView, CommentView, \
    ApplicationChoicesView, StatisticsView, SupervisorView, ApplicationFieldsView, AcademicYearView
from phdadmissions.views.documentations import FileView, DownloadView, ZipFileView, CsvFileView
from phdadmissions.views.search import ApplicationSearchView
from phdadmissions.views.users import StaffRoleView, StaffView

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
    url(r'^admin/staff_roles', StaffRoleView.as_view()),
    url(r'^admin/staff', StaffView.as_view()),
    url(r'^admin/academic_year', AcademicYearView.as_view()),
)
