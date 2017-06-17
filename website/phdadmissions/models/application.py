from django.core.validators import RegexValidator
from django.db import models

from assets.constants import *
from phdadmissions.models.academic_year import AcademicYear

POSSIBLE_FUNDING_CHOICES = (
        (SELF, "Self"),
        (DTP, "DTP"),
        (CDT, "CDT"),
        (PROJECT, "Project"),
        (XSCHOLARSHIP, "X-Scholarship"),
        (DOC, "DoC"),
        (OTHER, "Other")
    )

FUNDING_STATUS_CHOICES = (
        (PENDING, "Pending"),
        (AWARDED, "Awarded")
    )
ORIGIN_CHOICES = (
        (HOME, "Home"),
        (EU, "EU"),
        (OVERSEAS, "Overseas"),
        (QUERY, "Query")
    )
STUDENT_TYPE_CHOICES = (
        (COMPUTING, "Computing"),
        (CDT_STUDENT, "CDT Student Type"),
        (COMPUTING_AND_CDT, "Both Computing and CDT student")
    )
STATUS_CHOICES = (
        (PENDING_STATUS, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (REJECT_TO_MSC, "Rejected to MSc"),
        (WITHDRAWN, "Withdrawn"),
        (DEFERRED, "Deferred")
    )
GENDER_CHOICES = (
        (FEMALE, "Female"),
        (MALE, "Male")
    )


# Specifies the application of a student
class Application(models.Model):
    digits = RegexValidator(r'^[0-9]*$', 'Only digits are allowed.')

    # Basic
    registry_ref = models.CharField(max_length=100, validators=[digits], unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    surname = models.CharField(max_length=100)
    forename = models.CharField(max_length=100)
    possible_funding = models.CharField(max_length=100, choices=POSSIBLE_FUNDING_CHOICES)
    funding_status = models.CharField(max_length=100, choices=FUNDING_STATUS_CHOICES, default=PENDING)
    origin = models.CharField(max_length=100, choices=ORIGIN_CHOICES)
    student_type = models.CharField(max_length=100, choices=STUDENT_TYPE_CHOICES)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING_STATUS, blank=True)

    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)

    # Administration
    research_subject = models.CharField(max_length=255, null=True, blank=True)
    registry_comment = models.TextField(null=True, blank=True)

    academic_year = models.ForeignKey(AcademicYear, related_name='applications', null=False)



