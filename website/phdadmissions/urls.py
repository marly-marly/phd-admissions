from django.conf.urls import patterns, url

from phdadmissions.views.applications import ApplicationView, ApplicationFieldChoicesView, ApplicationVisibleFieldsView
from phdadmissions.views.academic_years import AcademicYearView
from phdadmissions.views.email import EmailConfigurationView, EmailPreviewView, SendEmailView
from phdadmissions.views.statistics import BasicStatisticsView, RatioStatisticsView, StaffStatisticsView, \
    ApplicationStatisticsView
from phdadmissions.views.supervisions import SupervisionView, SupervisionAllocationView
from phdadmissions.views.documentations import FileView, DownloadView, ZipFileView, CsvFileView
from phdadmissions.views.search import ApplicationSearchView
from phdadmissions.views.tags import TagsView, ApplicationTagsView
from phdadmissions.views.users import RecommendedSupervisorsView

urlpatterns = patterns(
    '',
    # Applications
    url(r'^application/$', ApplicationView.as_view()),
    url(r'^supervision/$', SupervisionView.as_view()),
    url(r'^supervision_allocation/$', SupervisionAllocationView.as_view()),
    url(r'^newFilesIndex/application/$', ApplicationFieldChoicesView.as_view()),
    url(r'^application_fields/$', ApplicationVisibleFieldsView.as_view()),
    url(r'^application/tags/$', ApplicationTagsView.as_view()),
    url(r'^recommended_supervisors/$', RecommendedSupervisorsView.as_view()),

    # Search
    url(r'^search/$', ApplicationSearchView.as_view()),

    # Statistics
    url(r'^statistics/applications/$', ApplicationStatisticsView.as_view()),
    url(r'^statistics/staff/$', StaffStatisticsView.as_view()),
    url(r'^statistics/ratios/$', RatioStatisticsView.as_view()),
    url(r'^statistics/$', BasicStatisticsView.as_view()),

    # Files
    url(r'^file/$', FileView.as_view()),
    url(r'^download/$', DownloadView.as_view()),
    url(r'^csv_download/$', CsvFileView.as_view()),
    url(r'^zip_download/$', ZipFileView.as_view()),

    # Admin
    url(r'^admin/academic_year', AcademicYearView.as_view()),
    url(r'^admin/tags', TagsView.as_view()),
    url(r'^admin/email/$', EmailConfigurationView.as_view()),
    url(r'^admin/email_preview/$', EmailPreviewView.as_view()),
    url(r'^admin/email_send/$', SendEmailView.as_view()),
)
