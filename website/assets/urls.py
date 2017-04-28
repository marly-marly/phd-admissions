from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^api/', include('phdadmissions.urls')),
    url(r'^api/', include('authentication.urls')),
    url(r'^admin/', include(admin.site.urls))
)

# development static media server
if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )