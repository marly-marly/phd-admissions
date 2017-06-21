import os

from django.db import models
from django.dispatch import receiver

from assets.constants import *
from assets.settings import MEDIA_ROOT
from phdadmissions.models.supervision import Supervision

SUB_FOLDER = 'applications/documentation/'


# Gives a unique name to each file
def content_file_name(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    path = SUB_FOLDER + str(instance.supervision.application.registry_ref) + "/" + str(
        instance.file_type) + "_" + filename

    # Give a unique name using (number) at the end of the filename
    temp_path = path
    counter = 1
    file_absolute = MEDIA_ROOT + "/" + temp_path + file_extension
    while os.path.exists(file_absolute):
        temp_path = path
        temp_path += " (%d)" % counter
        file_absolute = MEDIA_ROOT + "/" + temp_path + file_extension
        counter += 1

    return temp_path + file_extension


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
    description = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


@receiver(models.signals.post_delete, sender=Documentation)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=Documentation)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Documentation.objects.get(pk=instance.pk).file
    except Documentation.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
