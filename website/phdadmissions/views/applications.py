import json

from django.http.response import HttpResponse
from rest_framework import status, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from authentication.roles import roles
from django.template import loader

from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.models.application import Application, POSSIBLE_FUNDING_CHOICES, FUNDING_STATUS_CHOICES, \
    ORIGIN_CHOICES, STATUS_CHOICES, STUDENT_TYPE_CHOICES
from assets.constants import ADMIN, SUPERVISOR
from phdadmissions.models.documentation import Documentation
from phdadmissions.models.supervision import Supervision, RECOMMENDATION_CHOICES
from django.contrib.auth.models import User
from phdadmissions.models.comment import Comment
from phdadmissions.serializers.academic_year_serializer import AcademicYearSerializer

from phdadmissions.serializers.application_serializer import ApplicationSerializer

from phdadmissions.serializers.comment_serializer import CommentSerializer
from phdadmissions.serializers.supervision_serializer import SupervisionSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request

# Returns the default home page
from phdadmissions.utilities.helper_functions import get_model_fields


class IndexView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        template = loader.get_template('phdadmissions/index.html')

        return HttpResponse(template.render())


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

        supervisors = json_data['supervisors']

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


class ApplicationChoicesView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Gets all field newFilesIndex available for a PhD application
    def get(self, request):
        choices = {
            "possible_funding": {item[0]: item[1] for item in POSSIBLE_FUNDING_CHOICES},
            "funding_status": {item[0]: item[1] for item in FUNDING_STATUS_CHOICES},
            "origin": {item[0]: item[1] for item in ORIGIN_CHOICES},
            "student_type": {item[0]: item[1] for item in STUDENT_TYPE_CHOICES},
            "status": {item[0]: item[1] for item in STATUS_CHOICES},
            "recommendation": {item[0]: item[1] for item in RECOMMENDATION_CHOICES}
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
                return throw_bad_request("Application was not found with the id: " + str(application_id))

            supervisor_username = data.get('supervisor', None)
            supervisor = User.objects.filter(username=supervisor_username).first()
            if not supervisor:
                return throw_bad_request("Supervisor was not find with the username: " + str(supervisor_username))

            new_supervision = Supervision.objects.create(application=application, supervisor=supervisor)
            supervision_serializer = SupervisionSerializer(new_supervision)
            json_response = JSONRenderer().render(supervision_serializer.data)

            return HttpResponse(json_response, content_type='application/json')

        # TODO: make this a delete request
        if action == "DELETE":
            user = request.user
            if user.role != roles.ADMIN:
                return throw_bad_request("No sufficient permission.")

            supervision_id = data.get('supervision_id', None)
            if not supervision_id:
                return throw_bad_request("No supervision was specified.")

            supervision = Supervision.objects.filter(id=supervision_id).first()
            if not supervision:
                return throw_bad_request("Supervision could not be found with the id: " + str(supervision_id))

            if request.user.role == roles.ADMIN:
                supervision.delete()
            else:
                return throw_bad_request("No permission to delete supervision.")

        json_response = JSONRenderer().render({"success": True})

        return HttpResponse(json_response, content_type='application/json')

    # Updates an existing Supervision instance
    def put(self, request):
        data = request.data
        supervision_id = data.get('supervision_id', None)

        if not supervision_id:
            return throw_bad_request("No supervision was specified.")

        supervision = Supervision.objects.filter(id=supervision_id).first()
        if not supervision:
            return throw_bad_request("Supervision could not be found with the id " + str(supervision_id))

        # TODO check user roles here
        supervision_serializer = SupervisionSerializer(instance=supervision, data=data["supervision"], partial=True)
        if not supervision_serializer.is_valid():
            return throw_bad_request("Posted data was invalid.")
        supervision_serializer.save()

        return Response(status=status.HTTP_200_OK)


class CommentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Adds a new comment to a supervision
    def post(self, request):

        data = request.data
        supervision_id = data.get('supervision_id', None)
        if not supervision_id:
            # TODO: Create new ADMIN supervision, and add comment to that.
            return throw_bad_request("No supervision was specified.")

        supervision = Supervision.objects.filter(id=supervision_id).first()
        if not supervision:
            return throw_bad_request("No supervision could be found with the id " + str(supervision_id))

        if request.user == supervision.supervisor:
            content = data.get('content', None)
            if not content:
                return throw_bad_request("No content was specified for the comment.")

            new_comment = Comment.objects.create(supervision=supervision, content=content)
            comment_serializer = CommentSerializer(new_comment)
            json_response = JSONRenderer().render(comment_serializer.data)

            return HttpResponse(json_response, content_type='application/json')

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

        application_status = request.GET.getlist('status')
        possible_funding = request.GET.getlist('possible_funding')
        funding_status = request.GET.getlist('funding_status')
        origin = request.GET.getlist('origin')
        student_type = request.GET.getlist('student_type')

        academic_year_name = request.GET.get('academic_year_name', None)

        applications = Application.objects.filter(registry_ref__icontains=registry_ref, surname__icontains=surname,
                                                  forename__icontains=forename).prefetch_related("supervisions",
                                                                                                 "supervisions__supervisor",
                                                                                                 "supervisions__comments",
                                                                                                 "supervisions__documentations")
        if academic_year_name:
            applications = applications.filter(academic_year__name=academic_year_name)

        if len(application_status) > 0:
            applications = applications.filter(status__in=application_status)

        if len(possible_funding) > 0:
            applications = applications.filter(possible_funding__in=possible_funding)

        if len(funding_status) > 0:
            applications = applications.filter(funding_status__in=funding_status)

        if len(origin) > 0:
            applications = applications.filter(origin__in=origin)

        if len(student_type) > 0:
            applications = applications.filter(student_type__in=student_type)

        application_serializer = ApplicationSerializer(applications, many=True)
        json_response = JSONRenderer().render({"applications": application_serializer.data})

        return HttpResponse(json_response, content_type='application/json')


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
            "registry_comment"
        ]

        json_response = json.dumps(
            {"application_fields": application_fields, "default_fields": application_default_fields,
             "excluded_fields": fields_to_exclude})

        return HttpResponse(json_response, content_type='application/json')


class StatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns various statistics calculated from the application entities
    def get(self, request):
        current_academic_year = AcademicYear.objects.filter(default=True).first()
        if not current_academic_year:
            throw_bad_request("Please select a default academic year!")

        number_of_applications = Application.objects.filter(academic_year=current_academic_year).count()
        current_academic_year_json = AcademicYearSerializer(current_academic_year).data

        json_response = JSONRenderer().render(
            {"number_of_applications": number_of_applications, "current_academic_year": current_academic_year_json})

        return HttpResponse(json_response, content_type='application/json')


class SupervisorView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns the list of supervisor usernames
    def get(self, request):
        usernames = User.objects.filter(role__name=SUPERVISOR).values_list('username', flat=True)

        json_response = JSONRenderer().render({"usernames": usernames})

        return HttpResponse(json_response, content_type='application/json')


class AcademicYearView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns all the academic years from the database
    def get(self, request):
        academic_years = AcademicYear.objects.all()
        academic_year_serializer = AcademicYearSerializer(academic_years, many=True)
        json_response = JSONRenderer().render({"academic_years": academic_year_serializer.data})

        return HttpResponse(json_response, content_type='application/json')

    # Uploads a new academic year to the database
    def post(self, request):

        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        academic_year_serializer = AcademicYearSerializer(data=request.data)
        if not academic_year_serializer.is_valid():
            return throw_bad_request("Posted data was invalid.")

        academic_year_serializer.save()

        return Response(status=status.HTTP_201_CREATED)

    # Updates a new academic year in the database
    def put(self, request):

        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = request.data
        id = data.get('id', None)
        existing_academic_year = AcademicYear.objects.filter(id=id).first()
        if not existing_academic_year:
            return throw_bad_request("No academic year exists with the ID: " + str(id))

        academic_year = data.get('academic_year', None)
        if not academic_year:
            return throw_bad_request("No academic year was specified.")

        academic_year_serializer = AcademicYearSerializer(instance=existing_academic_year, data=academic_year,
                                                          partial=True)
        if not academic_year_serializer.is_valid():
            return throw_bad_request("Posted data was invalid.")

        academic_year_serializer.save()

        return Response({"id": existing_academic_year.id}, status=status.HTTP_200_OK)

    # Deletes an existing academic year
    def delete(self, request):
        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = json.loads(request.body.decode('utf-8'))
        id = data.get('id')

        if not id:
            return throw_bad_request("Academic Year id was not provided as a GET parameter.")

        academic_year = AcademicYear.objects.filter(id=id).first()
        if not academic_year:
            return throw_bad_request("Academic Year was not find with the ID." + str(id))

        academic_year.delete()

        return HttpResponse(status=204)
