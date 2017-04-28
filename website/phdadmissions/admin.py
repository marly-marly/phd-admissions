from django.contrib import admin
from tagging.registry import register

# Register your models here.
from phdadmissions.models.application import Application
from phdadmissions.models.supervision import Supervision

admin.site.register(Application)
admin.site.register(Supervision)

# Register model for tagging purpose
register(Application)
