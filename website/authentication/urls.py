from rest_framework_nested import routers
from authentication.views import LoginView, LogoutView, RestrictedView, RegistrationView
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^auth/register/$', RegistrationView.as_view(), name='register'),
    url(r'^auth/login/$', LoginView.as_view(), name='login'),
    url(r'^auth/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^auth/get_token/$', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^auth/authenticated/$', RestrictedView.as_view(), name='test_token'),
    url(r'^admin/', include(admin.site.urls)),
)
