import html2text
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from datetime import datetime
from multiselectfield import MultiSelectField

from assets.constants import *
from assets.constants import SUPERVISOR
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

    surname = models.CharField(max_length=100)
    forename = models.CharField(max_length=100)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)
    research_subject = models.CharField(max_length=255, null=True, blank=True)
    possible_funding = MultiSelectField(choices=POSSIBLE_FUNDING_CHOICES)
    funding_status = models.CharField(max_length=100, choices=FUNDING_STATUS_CHOICES, default=PENDING)
    origin = models.CharField(max_length=100, choices=ORIGIN_CHOICES)
    student_type = models.CharField(max_length=100, choices=STUDENT_TYPE_CHOICES)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING_STATUS, blank=True)

    # Administration
    administrator_comment = models.TextField(null=True, blank=True)
    phd_admission_tutor_comment = models.TextField(null=True, blank=True)

    academic_year = models.ForeignKey(AcademicYear, related_name='applications', null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


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


# Returns the value of various fields of an Application object, given an Application field as a string.
def get_application_field_value(application, field, remove_html=False):
    if field == "supervisions":
        supervisors = []
        for supervision in application.supervisions.all():
            if supervision.type == SUPERVISOR:
                supervisors.append(supervision.supervisor.first_name + " " + supervision.supervisor.last_name)

        supervisors_text = ", ".join(supervisors)

        return supervisors_text
    elif field == "academic_year":

        return application.academic_year.name
    elif field == "created_at":

        return application.created_at.strftime("%Y-%m-%d")
    elif field == "modified_at":

        return application.modified_at.strftime("%Y-%m-%d")
    elif field == "tags":
        tags = []
        for tag in application.tags.all():
            tags.append(tag.name)

        tags_text = ", ".join(tags)

        return tags_text
    elif remove_html and field == "administrator_comment":

        return html2text.html2text(application.administrator_comment)
    elif remove_html and field == "phd_admission_tutor_comment":

        return html2text.html2text(application.phd_admission_tutor_comment)
    else:

        return getattr(application, field)