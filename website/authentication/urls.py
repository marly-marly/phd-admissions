from authentication.views import LoginView, LogoutView, RestrictedView, StaffRoleView, \
    StaffSynchronisationView, SupervisorStaffView, SupervisorView, StaffView
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^get_token/$', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^authenticated/$', RestrictedView.as_view(), name='test_token'),

    # Users
    url(r'^staff_roles/$', StaffRoleView.as_view()),
    url(r'^sync_staff/$', StaffSynchronisationView.as_view()),
    url(r'^all_staff/$', StaffView.as_view()),
    url(r'^supervisor_staff/$', SupervisorStaffView.as_view()),
    url(r'^supervisor_usernames/$', SupervisorView.as_view()),
)
