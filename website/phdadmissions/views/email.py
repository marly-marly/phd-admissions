import html2text
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.html import strip_tags
from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from assets.constants import EMAIL, PENDING, EU, COMPUTING, PENDING_STATUS, FEMALE
from authentication.roles import roles
from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.models.application import Application, get_application_field_value
from phdadmissions.models.configuration import Configuration
from phdadmissions.models.supervision import Supervision
from phdadmissions.serializers.configuration_serializer import ConfigurationSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request
from phdadmissions.utilities.helper_functions import get_model_fields
import re


class EmailConfigurationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns the email configuration
    def get(self, request):

        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        email_configuration = Configuration.objects.filter(name=EMAIL).first()
        if email_configuration is None:
            email_configuration = Configuration.objects.create(name=EMAIL, value="")

        email_configuration_serializer = ConfigurationSerializer(email_configuration)
        json_response = JSONRenderer().render(email_configuration_serializer.data)

        return HttpResponse(json_response, content_type='application/json')

    # Updates the email configuration
    def put(self, request):

        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        email_configuration = Configuration.objects.filter(name=EMAIL).first()
        if email_configuration is None:
            return throw_bad_request("No email configuration exists yet.")

        data = request.data
        value = data.get('value', None)
        email_configuration_serializer = ConfigurationSerializer(instance=email_configuration, data={'value': value},
                                                                 partial=True)
        if not email_configuration_serializer.is_valid():
            return throw_bad_request("Posted data was invalid.")

        email_configuration_serializer.save()

        return Response(status=status.HTTP_200_OK)


class EmailPreviewView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns a preview HTML text of an example supervisor email
    def post(self, request):

        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = request.data
        email_template = data.get('email_template', None)
        if email_template is None:
            throw_bad_request("First you have to create an email template.")

        supervision_id = data.get('supervision_id', None)
        if supervision_id is None:
            # Set up a sample application
            academic_year = AcademicYear.objects.filter(default=True).first()
            if academic_year is None:
                throw_bad_request("First you have to create an academic year.")

            administrator_comment = "<div>" \
                                    "<b> Very strong application </b>" \
                                    "<p> She has got a good overall GPA, and she has experience in Physics." \
                                    "I certainly recommend her as a PhD student </p>" \
                                    "</div>"

            phd_admission_tutor_comment = "<div>" \
                                          "<b> Indeed very good application </b>" \
                                          "<p> I agree with the administrator." \
                                          "I certainly recommend her as a PhD student </p>" \
                                          "</div>"

            application = Application(id=1, academic_year=academic_year, registry_ref="012983234", surname="Szeles",
                                      forename="Yeesha",
                                      possible_funding=None, funding_status=PENDING, origin=EU,
                                      student_type=COMPUTING, status=PENDING_STATUS,
                                      research_subject="Investigating travelling at the speed of light.",
                                      administrator_comment=administrator_comment,
                                      phd_admission_tutor_comment=phd_admission_tutor_comment, gender=FEMALE)

            supervisor = User(username="Atrus", first_name="Atrus", last_name="Saavedro", email="atrus@mail.com")
        else:
            supervision = Supervision.objects.filter(id=supervision_id).first()
            if supervision is None:
                throw_bad_request("Supervision could not be found with the id " + str(supervision_id))

            application = supervision.application
            supervisor = supervision.supervisor

        generated_email = generate_email_content(email_template, application, request, supervisor)

        return HttpResponse(generated_email)


class SendEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Sends an email to a particular supervisor
    def post(self, request):
        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = request.data
        email_template = data.get('email_template', None)
        if email_template is None:
            throw_bad_request("First you have to create an email template.")

        supervision_id = data.get('supervision_id', None)
        if supervision_id is None:
            throw_bad_request("Supervision ID was not specified.")

        supervision = Supervision.objects.filter(id=supervision_id).first()
        if supervision is None:
            throw_bad_request("Supervision could not be found with the id " + str(supervision_id))

        application = supervision.application
        supervisor = supervision.supervisor
        generated_email = generate_email_content(email_template, application, request, supervisor)

        # Strip the html, so people will have the text as well
        text_content = html2text.html2text(generated_email)

        subject = 'PhD Admissions: {} {} ({})'.format(application.forename, application.surname, application.registry_ref)
        from_email = user.email
        to = supervisor.email

        # Create the email, and attach the HTML version as well
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(generated_email, "text/html")
        msg.send()

        return HttpResponse(status=status.HTTP_200_OK)


def generate_email_content(email_template, application, request, supervisor):
    generated_email = email_template
    application_fields = get_model_fields(Application)
    for application_field in application_fields:
        field_value = get_application_field_value(application, application_field)
        field_value = str(field_value)
        generated_email = re.sub(r'\{\{' + application_field + '\}\}', field_value, generated_email)

    generated_email = re.sub(r'\{\{supervisor_first_name\}\}', supervisor.first_name, generated_email)
    generated_email = re.sub(r'\{\{supervisor_last_name\}\}', supervisor.last_name, generated_email)

    if request is not None:
        application_url = request.build_absolute_uri(
            '/application/edit/' + str(application.id) + '/' + application.registry_ref)
        application_link = "<a target='blank' href='{}'>{}</a>".format(application_url, application_url)
        generated_email = re.sub(r'\{\{application_link\}\}', application_link, generated_email)

    return generated_email
