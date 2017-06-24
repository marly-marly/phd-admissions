import json

from django.contrib.auth.models import User
from django.http.response import HttpResponse
from rest_framework import status, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from tagging.models import Tag

from assets.constants import ADMIN
from authentication.roles import roles
from phdadmissions.models.application import Application, POSSIBLE_FUNDING_CHOICES, FUNDING_STATUS_CHOICES, \
    ORIGIN_CHOICES, STATUS_CHOICES, STUDENT_TYPE_CHOICES, GENDER_CHOICES
from phdadmissions.models.documentation import Documentation
from phdadmissions.models.supervision import Supervision, RECOMMENDATION_CHOICES
from phdadmissions.serializers.application_serializer import ApplicationSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request
from phdadmissions.utilities.helper_functions import get_model_fields


class ApplicationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Uploads a new PhD application
    def post(self, request):
        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        application = request.data["application"]
        json_data = json.loads(application)

        application_serializer = ApplicationSerializer(data=json_data)
        if not application_serializer.is_valid():
            return throw_bad_request("Posted data was invalid.")

        application = application_serializer.save()

        # Manage supervisions
        supervisors = json_data['supervisors']
        if len(supervisors) != 0:
            supervisor_objects = User.objects.filter(username__in=supervisors)
            [Supervision.objects.create(application=application, supervisor=supervisor_object) for supervisor_object
             in supervisor_objects]

        # Create Admin supervision, which is default for all applications
        admin_supervision = Supervision.objects.create(application=application, supervisor=request.user, type=ADMIN,
                                                       creator=True)

        # Manage documentation
        file_descriptions = json_data['file_descriptions']
        files = request.FILES
        if files:
            for key in files:
                # Find the last occurrence of "_"
                file_type = key[:key.rfind('_')]
                file = files[key]
                file_description = file_descriptions[key] if key in file_descriptions else ""
                Documentation.objects.create(supervision=admin_supervision, file=file, file_name=file.name,
                                             file_type=file_type, description=file_description)

        # Manage tagging
        if 'tag_words' in json_data:
            tags = json_data['tag_words']
            tags_string = ",".join(tags)
            Tag.objects.update_tags(application, tags_string)

        return Response({"id": application.id, "registry_ref": application.registry_ref},
                        status=status.HTTP_201_CREATED)

    # Edits an existing PhD application
    def put(self, request):
        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = request.data
        id = data.get('id', None)
        existing_application = Application.objects.filter(id=id).first()
        if not existing_application:
            return throw_bad_request("No application exists with the ID: " + str(id))

        application = data.get('application', None)
        if not application:
            return throw_bad_request("No application was specified.")

        application_serializer = ApplicationSerializer(instance=existing_application, data=application, partial=True)
        if not application_serializer.is_valid():
            return throw_bad_request("Posted data was invalid.")
        application_serializer.save()

        return Response({"id": existing_application.id, "registry_ref": existing_application.registry_ref},
                        status=status.HTTP_200_OK)

    # Gets the details of a specific PhD application
    def get(self, request):
        id = request.GET.get('id', None)

        if not id:
            return throw_bad_request("PhD Application id was not provided as a GET parameter.")

        application = Application.objects.filter(id=id).first()
        if not application:
            return throw_bad_request("PhD Application was not find with the ID." + str(id))

        application_serializer = ApplicationSerializer(application)
        json_response = JSONRenderer().render({"application": application_serializer.data})

        return HttpResponse(json_response, content_type='application/json')

    # Deletes an existing application
    def delete(self, request):
        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = json.loads(request.body.decode('utf-8'))
        id = data.get('id')

        if not id:
            return throw_bad_request("PhD Application id was not provided as a GET parameter.")

        application = Application.objects.filter(id=id).first()
        if not application:
            return throw_bad_request("PhD Application was not find with the ID." + str(id))

        application.delete()

        return HttpResponse(status=204)


class ApplicationFieldChoicesView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Gets all field newFilesIndex available for a PhD application
    def get(self, request):
        # TODO: Generalise?
        choices = {
            "possible_funding": {item[0]: item[1] for item in POSSIBLE_FUNDING_CHOICES},
            "funding_status": {item[0]: item[1] for item in FUNDING_STATUS_CHOICES},
            "origin": {item[0]: item[1] for item in ORIGIN_CHOICES},
            "student_type": {item[0]: item[1] for item in STUDENT_TYPE_CHOICES},
            "status": {item[0]: item[1] for item in STATUS_CHOICES},
            "recommendation": {item[0]: item[1] for item in RECOMMENDATION_CHOICES},
            "gender": {item[0]: item[1] for item in GENDER_CHOICES}
        }

        response_data = json.dumps(choices)
        return HttpResponse(response_data, content_type='application/json')


class ApplicationFieldsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns all the fields of the application model
    def get(self, request):
        application_fields = get_model_fields(Application)

        # TODO Make this dynamic
        # Default fields are the ones to display/include by default on the UI/in files.
        application_default_fields = [
            "registry_ref",
            "created_at",
            "surname",
            "forename",
            "research_subject",
            "possible_funding",
            "origin"
        ]

        fields_to_exclude = [
            "id",
            "administrator_comment",
            "phd_admission_tutor_comment"
        ]

        json_response = json.dumps(
            {"application_fields": application_fields, "default_fields": application_default_fields,
             "excluded_fields": fields_to_exclude})

        return HttpResponse(json_response, content_type='application/json')


