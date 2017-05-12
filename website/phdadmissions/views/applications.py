import json

from django.http.response import HttpResponseBadRequest, HttpResponse
from rest_framework import status, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from authentication.roles import roles
from django.template import loader

from phdadmissions.models.application import Application, POSSIBLE_FUNDING_CHOICES, FUNDING_STATUS_CHOICES, \
    ORIGIN_CHOICES, STATUS_CHOICES, STUDENT_TYPE_CHOICES
from assets.constants import ADMIN
from phdadmissions.models.documentation import Documentation
from phdadmissions.models.supervision import Supervision
from django.contrib.auth.models import User
from phdadmissions.models.comment import Comment

from phdadmissions.serializers.application_serializer import ApplicationSerializer


# Returns the default home page
class IndexView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        template = loader.get_template('phdadmissions/index.html')

        return HttpResponse(template.render())


class ApplicationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Uploads a new or edits an existing PhD application
    def post(self, request):

        application = request.data["application"]
        json_data = json.loads(application)

        new = json_data['new']
        supervisors = json_data['supervisors']

        if new:
            application_serializer = ApplicationSerializer(data=json_data)
            if not application_serializer.is_valid():
                return throw_bad_request("Posted data was invalid.")

            application = application_serializer.save()

            # Manage supervisions
            if len(supervisors) != 0:
                supervisor_objects = User.objects.filter(username__in=supervisors)
                [Supervision.objects.create(application=application, supervisor=supervisor_object) for supervisor_object
                 in supervisor_objects]

            # Create Admin supervision, which is default for all applications
            admin_supervision = Supervision.objects.create(application=application, supervisor=request.user, type=ADMIN)

            # Manage documentation
            files = request.FILES
            if files:
                for key in files:
                    # Find the last occurrence of "_"
                    file_type = key[:key.rfind('_')]
                    Documentation.objects.create(supervision=admin_supervision, file=files[key], file_type=file_type)
        else:
            id = json_data['id']
            application = Application.objects.filter(id=id).first()
            if not application:
                return throw_bad_request("No application exists with the ID: " + str(id))

            application_serializer = ApplicationSerializer(instance=application, data=json_data, partial=True)
            if not application_serializer.is_valid():
                return throw_bad_request("Posted data was invalid.")
            application_serializer.save()

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


class ApplicationChoicesView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Gets all field additionals available for a PhD application
    def get(self, request):
        choices = {
            "possible_funding": {item[0]: item[1] for item in POSSIBLE_FUNDING_CHOICES},
            "funding_status": {item[0]: item[1] for item in FUNDING_STATUS_CHOICES},
            "origin": {item[0]: item[1] for item in ORIGIN_CHOICES},
            "student_type": {item[0]: item[1] for item in STUDENT_TYPE_CHOICES},
            "status": {item[0]: item[1] for item in STATUS_CHOICES}
        }

        response_data = json.dumps(choices)
        return HttpResponse(response_data, content_type='application/json')


class SupervisionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Adds/Removes a new supervision to/from a specific application
    def post(self, request):

        data = request.data
        action = data.get('action', None)
        if not action:
            return throw_bad_request("No action was specified.")

        if action == "ADD":
            application_id = data.get('id', None)
            application = Application.objects.filter(id=application_id).first()
            if not application:
                return throw_bad_request("Application was not find with the id" + str(application_id))

            supervisor_username = data.get('supervisor', None)
            supervisor = User.objects.filter(username=supervisor_username).first()
            if not supervisor:
                return throw_bad_request("Supervisor was not find with the username" + str(supervisor_username))

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


class ApplicationSearchView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Gets those applications that correspond to the provided search criteria
    def get(self, request):
        registry_ref = request.GET.get('registry_ref', "")
        surname = request.GET.get('surname', "")
        forename = request.GET.get('forename', "")
        # TODO: Include date-range

        application_status = request.GET.get('status', None)
        possible_funding = request.GET.get('possible_funding', None)
        funding_status = request.GET.get('funding_status', None)
        origin = request.GET.get('origin', None)
        student_type = request.GET.get('student_type', None)

        applications = Application.objects.filter(registry_ref__icontains=registry_ref, surname__icontains=surname,
                                                  forename__icontains=forename)

        if application_status:
            applications = applications.filter(status=application_status)

        if possible_funding:
            applications = applications.filter(possible_funding=possible_funding)

        if funding_status:
            applications = applications.filter(funding_status=funding_status)

        if origin:
            applications = applications.filter(origin=origin)

        if student_type:
            applications = applications.filter(student_type=student_type)

        application_serializer = ApplicationSerializer(applications, many=True)
        json_reponse = JSONRenderer().render({"applications": application_serializer.data})

        return HttpResponse(json_reponse, content_type='application/json')


class StatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns various statistics calculated from the application entities
    def get(self, request):

        number_of_applications = Application.objects.count()

        json_response = JSONRenderer().render({"number_of_applications": number_of_applications})

        return HttpResponse(json_response, content_type='application/json')


def throw_bad_request(error_message):
    response_data = json.dumps({"error": error_message})

    return HttpResponseBadRequest(response_data, content_type='application/json')
