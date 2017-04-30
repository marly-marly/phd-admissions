from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from phdadmissions.views.applications import IndexView

urlpatterns = patterns(
    '',
    url(r'^api/applications/', include('phdadmissions.urls')),
    url(r'^api/auth/', include('authentication.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^silk/', include('silk.urls', namespace='silk')),
    url('^.*$', IndexView.as_view(), name='index')
)

# development static media server
if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )