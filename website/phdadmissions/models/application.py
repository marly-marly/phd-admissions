from django.core.validators import RegexValidator
from django.db import models

from assets.constants import *


# Specifies the application of a student
class Application(models.Model):
    digits = RegexValidator(r'^[0-9]*$', 'Only digits are allowed.')

    # Basic
    registry_ref = models.CharField(max_length=100, validators=[digits])
    surname = models.CharField(max_length=100)
    forename = models.CharField(max_length=100)

    POSSIBLE_FUNDING_CHOICES = (
        (SELF, "Self"),
        (DTP, "DTP"),
        (CDT, "CDT"),
        (PROJECT, "Project"),
        (XSCHOLARSHIP, "X-Scholarship"),
        (DOC, "DoC"),
        (OTHER, "Other")
    )
    possible_funding = models.CharField(max_length=100, choices=POSSIBLE_FUNDING_CHOICES)

    FUNDING_STATUS_CHOICES = (
        (PENDING, "Pending"),
        (AWARDED, "Awarded")
    )
    funding_status = models.CharField(max_length=100, choices=FUNDING_STATUS_CHOICES, default=PENDING)

    ORIGIN_CHOICES = (
        (HOME, "Home"),
        (EU, "EU"),
        (OVERSEAS, "Overseas"),
        (QUERY, "Query")
    )
    origin = models.CharField(max_length=100, choices=ORIGIN_CHOICES)

    STUDENT_TYPE_CHOICES = (
        (COMPUTING, "Computing"),
        (CDT_STUDENT, "CDT Student Type"),
        (COMPUTING_AND_CDT, "Both Computing and CDT student")
    )
    student_type = models.CharField(max_length=100, choices=STUDENT_TYPE_CHOICES)

    STATUS_CHOICES = (
        (PENDING_STATUS, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (REJECT_TO_MSC, "Rejected to MSc"),
        (WITHDRAWN, "Withdrawn")
    )
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING_STATUS, blank=True)

    # Administration
    research_subject = models.CharField(max_length=255, null=True)
    registry_comment = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
