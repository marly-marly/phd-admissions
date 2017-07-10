from django.contrib import admin
from tagging.registry import register

# Register your models here.
from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.models.application import Application
from phdadmissions.models.configuration import Configuration
from phdadmissions.models.documentation import Documentation
from phdadmissions.models.supervision import Supervision
from phdadmissions.models.comment import Comment

admin.site.register(Application)
admin.site.register(Supervision)
admin.site.register(Comment)
admin.site.register(Documentation)
admin.site.register(AcademicYear)
admin.site.register(Configuration)

# Register model for tagging purpose
register(Application)
