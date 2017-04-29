from django.contrib import admin
from tagging.registry import register

# Register your models here.
from phdadmissions.models.application import Application
from phdadmissions.models.supervision import Supervision
from phdadmissions.models.comment import Comment

admin.site.register(Application)
admin.site.register(Supervision)
admin.site.register(Comment)

# Register model for tagging purpose
register(Application)
