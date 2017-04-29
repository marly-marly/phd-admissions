import json

from django.http.response import HttpResponseBadRequest, HttpResponse
from rest_framework import status, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from authentication.roles import roles

from assets.constants import *
from phdadmissions.models.application import Application
from phdadmissions.models.supervision import Supervision
from django.contrib.auth.models import User
from phdadmissions.models.comment import Comment

from phdadmissions.serializers.application_serializer import ApplicationSerializer


class ApplicationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Uploads a new or edits an existing PhD application
    def post(self, request):

        data = request.data
        new = data.get('new', "True") == "True"

        registry_ref = data.get('registry_ref', None)
        surname = data.get('surname', None)
        forename = data.get('forename', None)
        possible_funding = data.get('possible_funding', None)
        funding_status = data.get('funding_status', None)
        origin = data.get('origin', None)

        student_type = data.get('student_type', None)
        research_subject = data.get('research_subject', None)
        registry_comment = data.get('registry_comment', None)

        application_status = data.get('status', PENDING_STATUS)

        supervisors = data.getlist('supervisors', [])

        if new:
            application = Application.objects.create(registry_ref=registry_ref, surname=surname, forename=forename,
                                                     possible_funding=possible_funding, funding_status=funding_status,
                                                     origin=origin,
                                                     student_type=student_type, research_subject=research_subject,
                                                     registry_comment=registry_comment, status=application_status)

            if len(supervisors) != 0:
                supervisor_objects = User.objects.filter(username__in=supervisors)
                [Supervision.objects.create(application=application, supervisor=supervisor_object) for supervisor_object
                 in supervisor_objects]
        else:
            id = data.get('id', None)
            application = Application.objects.filter(id=id).first()
            if not application:
                return throw_bad_request("No application exists with the ID: " + str(id))

            application.registry_ref = registry_ref
            application.surname = surname
            application.forename = forename
            application.possible_funding = possible_funding
            application.funding_status = funding_status
            application.origin = origin

            application.student_type = student_type
            application.research_subject = research_subject
            application.registry_comment = registry_comment

            application.status = application_status

            application.save()

        return Response(status=status.HTTP_201_CREATED)

    # Gets the details of a specific PhD application
    def get(self, request):
        id = request.GET.get('id', None)

        if not id:
            return throw_bad_request("PhD Application id was not provided as a GET parameter.")

        application = Application.objects.filter(id=id).first()
        if not application:
            return throw_bad_request("PhD Application was not find with the ID." + str(id))

        application_serializer = ApplicationSerializer(application)
        json_reponse = JSONRenderer().render({"application": application_serializer.data})

        return HttpResponse(json_reponse, content_type='application/json')


class SupervisionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Adds/Removes a new supervision to/from a specific application
    def post(self, request):

        data = request.data
        action = data.get('action', None)
        if not action:
            return throw_bad_request("No action was specified.")

        application_id = data.get('id', None)
        application = Application.objects.filter(id=application_id).first()
        if not application:
            return throw_bad_request("Application was not find with the id" + str(application_id))

        supervisor_username = data.get('supervisor', None)
        supervisor = User.objects.filter(username=supervisor_username).first()
        if not supervisor:
            return throw_bad_request("Supervisor was not find with the username" + str(supervisor_username))

        if action == "ADD":
            Supervision.objects.create(application=application, supervisor=supervisor)

        # TODO: make this a delete request
        if action == "DELETE":
            supervision_id = data.get('supervision_id', None)
            if not supervision_id:
                return throw_bad_request("No supervision was specified.")

            supervision = Supervision.objects.filter(id=supervision_id).first()
            if not supervision:
                return throw_bad_request("Supervision could not be found with the id " + str(supervision_id))

            if request.user.role == roles.ADMIN:
                supervision.delete()
            else:
                return throw_bad_request("No permission to delete supervision.")

        return HttpResponse("Success", content_type='application/json')


class CommentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Adds a new comment to a supervision
    def post(self, request):

        data = request.data
        supervision_id = data.get('supervision_id', None)
        if not supervision_id:
            return throw_bad_request("No supervision was specified.")

        supervision = Supervision.objects.filter(id=supervision_id).first()
        if not supervision:
            return throw_bad_request("No supervision could be found with the id " + str(supervision_id))

        if request.user == supervision.supervisor:
            content = data.get('content', None)
            if not content:
                return throw_bad_request("No content was specified for the comment.")

            Comment.objects.create(supervision=supervision, content=content)

            return HttpResponse("Success", content_type='application/json')

        return throw_bad_request("You have no permission to add a comment to this supervision.")


def throw_bad_request(error_message):
    response_data = json.dumps({"error": error_message})

    return HttpResponseBadRequest(response_data, content_type='application/json')
