import json

from django.contrib.auth.models import User
from django.http.response import HttpResponse
from rest_framework import status, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from tagging.models import Tag

from assets.constants import ADMIN, SUPERVISOR
from authentication.roles import roles
from phdadmissions.models.application import Application, POSSIBLE_FUNDING_CHOICES, FUNDING_STATUS_CHOICES, \
    ORIGIN_CHOICES, STATUS_CHOICES, STUDENT_TYPE_CHOICES, GENDER_CHOICES
from phdadmissions.models.documentation import Documentation
from phdadmissions.models.supervision import Supervision, RECOMMENDATION_CHOICES
from phdadmissions.serializers.application_serializer import ApplicationSerializer
from phdadmissions.serializers.documentation_serializer import DocumentationSerializer
from phdadmissions.serializers.supervision_serializer import SupervisionSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request, throw_invalid_data
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
            return throw_invalid_data(application_serializer.errors)

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
            for tag_name in tags:
                Tag.objects.add_tag(application, "\"" + tag_name + "\"")

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
            return throw_invalid_data(application_serializer.errors)
        application_serializer.save()

        return Response({"id": existing_application.id, "registry_ref": existing_application.registry_ref},
                        status=status.HTTP_200_OK)

    # Returns the details of a specific PhD application
    def get(self, request):
        id = request.GET.get('id', None)

        if not id:
            return throw_bad_request("PhD Application id was not provided as a GET parameter.")

        application = Application.objects.all().prefetch_related("supervisions",
                                                                 "supervisions__supervisor",
                                                                 "supervisions__documentations").filter(id=id).first()
        if not application:
            return throw_bad_request("PhD Application was not find with the ID." + str(id))

        application_serializer = ApplicationSerializer(application)

        # Organise the output to make access simper for the front-end
        admin_supervisions = []
        creator_supervision = None
        creator_supervision_files = {}
        supervisor_supervisions = []
        supervisor_supervision_files = {}
        supervisions = application.supervisions.all()
        for supervision in supervisions:
            if supervision.type == SUPERVISOR:
                supervisor_supervisions.append(supervision)

                # Documentations
                supervisor_supervision_files[supervision.id] = {}
                supervision_documentations = supervision.documentations.all()
                for documentation in supervision_documentations:
                    if documentation.file_type not in supervisor_supervision_files[supervision.id]:
                        supervisor_supervision_files[supervision.id][documentation.file_type] = []

                    supervisor_supervision_file_serializer = DocumentationSerializer(documentation)
                    supervisor_supervision_files[supervision.id][documentation.file_type].append(
                        supervisor_supervision_file_serializer.data)
                continue
            if supervision.type == ADMIN:
                admin_supervisions.append(supervision)
                if supervision.creator:
                    creator_supervision = supervision

                    # Documentations
                    supervision_documentations = supervision.documentations.all()
                    for documentation in supervision_documentations:
                        if documentation.file_type not in creator_supervision_files:
                            creator_supervision_files[documentation.file_type] = []

                        creator_supervision_file_serializer = DocumentationSerializer(documentation)
                        creator_supervision_files[documentation.file_type].append(
                            creator_supervision_file_serializer.data)
                continue

        # Serializers
        admin_supervision_serializer = SupervisionSerializer(admin_supervisions, many=True)
        creator_supervision_serializer = SupervisionSerializer(creator_supervision)
        supervisor_supervision_serializer = SupervisionSerializer(supervisor_supervisions, many=True)

        response = {
            "application": application_serializer.data,
            "admin_supervisions": admin_supervision_serializer.data,
            "creator_supervision": creator_supervision_serializer.data,
            "creator_supervision_files": creator_supervision_files,
            "supervisor_supervisions": supervisor_supervision_serializer.data,
            "supervisor_supervision_files": supervisor_supervision_files
        }
        json_response = JSONRenderer().render(response)

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

    # Returns all the allowed choices for various Application and Supervision model fields.
    def get(self, request):
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


class ApplicationVisibleFieldsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns specific fields of the application model
    def get(self, request):
        application_fields = get_model_fields(Application)

        # Extra fields are those that are not picked up by the inbuilt "get_fields" method.
        extra_fields = [
            "tags"
        ]

        # Default fields are the ones to display/include by default on the UI/in files.
        application_default_fields = [
            "registry_ref",
            "created_at",
            "surname",
            "forename",
            "research_subject",
            "possible_funding",
            "origin",
            "status",
            "supervisions"
        ]

        # Excluded fields are the ones without significance outside the specific application's page.
        fields_to_exclude = [
            "id"
        ]

        json_response = json.dumps(
            {"application_fields": application_fields, "default_fields": application_default_fields,
             "excluded_fields": fields_to_exclude, "extra_fields": extra_fields})

        return HttpResponse(json_response, content_type='application/json')
