from django.db import models
from assets.constants import *
from phdadmissions.models.supervision import Supervision


# Gives a unique name to each file
def content_file_name(instance, filename):
    # TODO: pre-fix with unique registry ref as well
    return 'applications/documentation/' + str(instance.supervision.application.registry_ref) + "/" + str(
        instance.file_type) + "_" + filename


# Specifies the details of uploaded files
class Documentation(models.Model):
    supervision = models.ForeignKey(Supervision, related_name='documentations', null=False)

    file = models.FileField(upload_to=content_file_name, null=True)
    file_name = models.CharField(max_length=255, null=True)

    # TODO Interview Report
    FILE_TYPE_CHOICES = (
        (APPLICATION_FORM, "Application form"),
        (RESEARCH_SUMMARY, "Research summary"),
        (REFERENCE, "Reference"),
        (ADDITIONAL_MATERIAL, "Additional material")
    )

    file_type = models.CharField(max_length=100, choices=FILE_TYPE_CHOICES, null=False)
    description = models.CharField(max_length=255, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
