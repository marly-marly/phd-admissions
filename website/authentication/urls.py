from rest_framework_nested import routers
from authentication.views import LoginView, LogoutView, RestrictedView, RegistrationView, StaffRoleView, \
    StaffSynchronisationView, SupervisorStaffView, SupervisorView, StaffView
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^register/$', RegistrationView.as_view(), name='register'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^get_token/$', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^authenticated/$', RestrictedView.as_view(), name='test_token'),

    url(r'^staff_roles/$', StaffRoleView.as_view()),
    url(r'^sync_staff/$', StaffSynchronisationView.as_view()),
    url(r'^supervisor_staff/$', SupervisorStaffView.as_view()),
    url(r'^supervisor/$', SupervisorView.as_view()),
    url(r'^staff/$', StaffView.as_view()),
)
