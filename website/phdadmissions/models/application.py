from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from datetime import datetime
from multiselectfield import MultiSelectField

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
    (CDT_STUDENT, "CDT"),
    (COMPUTING_AND_CDT, "Computing and CDT")
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
    possible_funding = MultiSelectField(choices=POSSIBLE_FUNDING_CHOICES)
    funding_status = models.CharField(max_length=100, choices=FUNDING_STATUS_CHOICES, default=PENDING)
    origin = models.CharField(max_length=100, choices=ORIGIN_CHOICES)
    student_type = models.CharField(max_length=100, choices=STUDENT_TYPE_CHOICES)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING_STATUS, blank=True)

    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)

    research_subject = models.CharField(max_length=255, null=True, blank=True)

    # Administration
    administrator_comment = models.TextField(null=True, blank=True)
    phd_admission_tutor_comment = models.TextField(null=True, blank=True)

    academic_year = models.ForeignKey(AcademicYear, related_name='applications', null=False)


# Sets the modified_now field of an application to "now"
def application_updated_now(application):
    application.modified_at = datetime.now()
    application.save()


# Helper method for finding Application objects that contain exactly "x" possible_funding
def application_with_possible_funding(applications, x):
    return applications.filter(Q(possible_funding__startswith=x + ',') | Q(possible_funding__endswith=',' + x) | Q(
        possible_funding__contains=',{0},'.format(x)) | Q(possible_funding=[x]))


def application_with_possible_funding_query(x):
    return [Q(possible_funding__startswith=x + ','), Q(possible_funding__endswith=',' + x), Q(
        possible_funding__contains=',{0},'.format(x)), Q(possible_funding=[x])]


def disjunction_applications_by_possible_funding(applications, possible_fundings):
    or_queries = []
    for possible_funding in possible_fundings:
        or_queries += (application_with_possible_funding_query(possible_funding))

    query = or_queries.pop()

    # Or the Q object with the ones remaining in the list
    for item in or_queries:
        query |= item

    return applications.filter(query)
