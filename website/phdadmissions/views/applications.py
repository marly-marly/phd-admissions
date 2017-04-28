import json

from django.http.response import HttpResponseBadRequest, HttpResponse
from rest_framework import status, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from assets.constants import *
from phdadmissions.models.application import Application
from phdadmissions.models.supervision import Supervision
from django.contrib.auth.models import User

from phdadmissions.serializers.application_serializer import ApplicationSerializer


class ApplicationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Uploads a new or edits an existing PhD application
    def post(self, request):

        # Read basic required parameters
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
                response_data = json.dumps({"error": "No application exists with the ID: " + str(id)})
                return HttpResponseBadRequest(response_data, content_type='application/json')

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
            response_data = json.dumps({"error": "PhD Application id was not provided as a GET parameter."})
            return HttpResponseBadRequest(response_data, content_type='application/json')

        application = Application.objects.filter(id=id).first()
        if not application:
            response_data = json.dumps({"error": "PhD Application was not find with the ID." + str(id)})
            return HttpResponseBadRequest(response_data, content_type='application/json')

        application_serializer = ApplicationSerializer(application)
        json_reponse = JSONRenderer().render({"application": application_serializer.data})

        return HttpResponse(json_reponse, content_type='application/json')