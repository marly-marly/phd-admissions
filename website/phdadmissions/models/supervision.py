from django.db import models

from assets.constants import *
from django.contrib.auth.models import User
from phdadmissions.models.application import Application


# Specifies the details of supervision of staff members
class Supervision(models.Model):

    application = models.ForeignKey(Application, related_name='supervisions', null=False)
    supervisor = models.OneToOneField(User, related_name='supervision')
    acceptance_condition = models.TextField(null=True)

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
    recommendation = models.CharField(max_length=100, choices=RECOMMENDATION_CHOICES, default=NOT_VIEWED)

    TYPE_CHOICES = (
        (ADMIN, "Administrator"),
        (SUPERVISOR, "Supervisor"),
        (SUPER_ADMIN, "Super Administrator")
    )

    type = models.CharField(max_length=100, choices=TYPE_CHOICES, default=SUPERVISOR)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


