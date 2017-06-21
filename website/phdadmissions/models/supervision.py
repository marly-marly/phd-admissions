from django.db import models

from assets.constants import *
from django.contrib.auth.models import User
from phdadmissions.models.application import Application

RECOMMENDATION_CHOICES = (
        (NOT_VIEWED, "Not viewed"),
        (WAIT_TO_INTERVIEW, "Wait to interview"),
        (REJECT_TO_MSC_RECOMMEND, "Reject to MSc"),
        (REJECT_TO_MAC_RECOMMEND, "Reject to MAC"),
        (STRAIGHT_REJECT, "Straight reject"),
        (ACCEPT_BUT_NOT_SUPERVISED, "Accept but not supervised"),
        (ACCEPT_AND_SUPERVISED, "Accept and supervised"),
        (OTHER_RECOMMEND, "Other")
    )


# Specifies the details of supervision of staff members
class Supervision(models.Model):

    application = models.ForeignKey(Application, related_name='supervisions', null=False)
    supervisor = models.ForeignKey(User, related_name='supervisions', null=False)
    acceptance_condition = models.TextField(null=True)
    recommendation = models.CharField(max_length=100, choices=RECOMMENDATION_CHOICES, default=NOT_VIEWED, blank=True)

    TYPE_CHOICES = (
        (ADMIN, "Administrator"),
        (SUPERVISOR, "Supervisor")
    )

    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default=SUPERVISOR)
    creator = models.BooleanField(null=False, default=False)

    allocated = models.BooleanField(null=False, default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        # In case users change roles, we don't want to lose their past supervisions.
        unique_together = (('type', 'application', 'supervisor'),)


