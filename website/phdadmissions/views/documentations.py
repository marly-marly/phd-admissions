import csv
import datetime
import io
import json

from django.http.response import HttpResponse
import jwt
import zipfile
from io import BytesIO
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication, jwt_get_username_from_payload
from rest_framework_jwt.settings import api_settings

from assets.constants import SUPERVISOR
from assets.settings import MEDIA_URL

from phdadmissions.models.application import Application, application_updated_now
from phdadmissions.models.documentation import Documentation, SUB_FOLDER
from phdadmissions.models.supervision import Supervision
from phdadmissions.serializers.documentation_serializer import DocumentationSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request
from phdadmissions.utilities.helper_functions import verify_authentication_token, get_model_fields
from authentication.roles import roles


class FileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Uploads a new file for an existing supervision
    def post(self, request):

        json_data = json.loads(request.data["details"])
        supervision_id = json_data["supervision_id"]
        supervision = Supervision.objects.filter(id=supervision_id).first()
        if not supervision:
            return throw_bad_request("Supervision was not found with ID " + str(supervision_id))

        file_descriptions = json_data['file_descriptions']
        files = request.FILES
        if len(files) == 0:
            return throw_bad_request("No files were submitted")

        new_files = []
        if files:
            for key in files:
                # Find the last occurrence of "_"
                file_type = key[:key.rfind('_')]
                file = files[key]
                file_description = file_descriptions[key] if key in file_descriptions else ""
                new_file = Documentation.objects.create(supervision=supervision, file=file, file_name=file.name,
                                                        file_type=file_type, description=file_description)
                new_files.append(new_file)

        # Reflect the update on the application
        application_updated_now(supervision.application)

        documentation_serializer = DocumentationSerializer(new_files, many=True)

        return Response({"documentations": documentation_serializer.data}, status=status.HTTP_201_CREATED)

    # Deletes an existing file from an existing supervision
    def delete(self, request):
        file_id = request.GET.get("file_id")

        if not file_id:
            return throw_bad_request("Documentation ID was not provided as a GET parameter.")

        documentation = Documentation.objects.filter(id=file_id).first()
        if not documentation:
            return throw_bad_request("Documentation was not find with the ID." + str(file_id))

        user = request.user
        if user.role != roles.ADMIN and user.username != documentation.supervision.supervisor.username:
            return throw_bad_request("No sufficient permission.")

        documentation.delete()

        return Response(status=status.HTTP_200_OK)


class DownloadView(APIView):
    permission_classes = (permissions.AllowAny,)

    # Serves a file for download, given the ID of the documentation
    def get(self, request):
        id = request.GET.get('id', None)
        token = request.GET.get('token', None)

        jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            return throw_bad_request("Signature has expired.")
        except jwt.DecodeError:
            return throw_bad_request("Error decoding signature.")

        username = jwt_get_username_from_payload(payload)

        if not username:
            return throw_bad_request("Invalid payload.")

        if not id:
            return throw_bad_request("Documentation ID was not provided as a GET parameter.")

        documentation = Documentation.objects.filter(id=id).first()
        if not documentation:
            return throw_bad_request("Documentation was not find with the ID." + str(id))

        response = HttpResponse(documentation.file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=' + documentation.file_name

        return response


class ZipFileView(APIView):
    permission_classes = (permissions.AllowAny,)

    # Serves a ZIP file for download, which contains the selected data of selected applications, including files.
    def get(self, request):

        token, application_ids, sort_field, sort_by, selected_fields = get_file_request_params(request)

        verified, error_msg = verify_authentication_token(token)
        if not verified:
            return throw_bad_request(error_msg)

        applications = Application.objects.filter(id__in=application_ids)

        # Open StringIO to grab in-memory ZIP contents
        zip_bytes_io = BytesIO()

        # The zip compressor
        zf = zipfile.ZipFile(zip_bytes_io, "w")

        # Organise the files into the ZIP
        for application in applications.all():
            for supervision in application.supervisions.all():
                for documentation in supervision.documentations.all():

                    # Path within the ZIP
                    zip_path = documentation.file.url
                    cropped_zip_path = zip_path.replace(MEDIA_URL + SUB_FOLDER, "", 1)

                    # Add file, at correct path
                    try:
                        zf.write(documentation.file.path, cropped_zip_path)
                    except OSError as e:
                        # TODO: log the error here
                        pass

        # CSV compressor
        csv_string_io = io.StringIO()
        csv_writer = csv.writer(csv_string_io, dialect='excel')
        write_to_csv_file(applications, csv_writer, selected_fields)

        # Write CSV to ZIP file
        zf.writestr("Application Details.csv", csv_string_io.getvalue())

        # Must close zip for all contents to be written
        zf.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        response = HttpResponse(zip_bytes_io.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename()

        return response


class CsvFileView(APIView):
    permission_classes = (permissions.AllowAny,)

    # Serves a CSV file for download, which contains the selected data of selected applications.
    def get(self, request):

        token, application_ids, sort_field, sort_by, selected_fields = get_file_request_params(request)

        verified, error_msg = verify_authentication_token(token)
        if not verified:
            return throw_bad_request(error_msg)

        applications = Application.objects.filter(id__in=application_ids)

        if sort_field and sort_by:
            new_sort_clause = sort_field if sort_by == 'ASC' else "-" + sort_field
            applications = applications.order_by(new_sort_clause)

        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="' + csv_filename() + '"'

        writer = csv.writer(response)
        write_to_csv_file(applications, writer, selected_fields)

        return response


def get_file_request_params(request):
    token = request.GET.get('token', None)
    application_ids = request.GET.getlist('application_ids')
    sort_field = request.GET.get('sort_field', None)
    sort_by = request.GET.get('sort_by', None)
    selected_fields = request.GET.getlist('selected_fields')

    return token, application_ids, sort_field, sort_by, selected_fields


def write_to_csv_file(applications, csv_writer, selected_fields):
    if not selected_fields:
        selected_fields = get_model_fields(Application)

    csv_writer.writerow(selected_fields)
    for application in applications:
        field_values = []
        for field in selected_fields:
            field_values.append(get_application_field_value(application, field))

        csv_writer.writerow(field_values)


def get_application_field_value(application, field):
    if field == "supervisions":
        supervisors = []
        for supervision in application.supervisions.all():
            if supervision.type == SUPERVISOR:
                supervisors.append(supervision.type + ": " + supervision.supervisor.username)

        supervisors_text = " ".join(supervisors)

        return supervisors_text
    elif field == "academic_year":

        return application.academic_year.name
    else:

        return getattr(application, field)


def csv_filename():
    current_date_string = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    return current_date_string + " Application Details.csv"


def zip_filename():
    current_date_string = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    return current_date_string + " Application Details.zip"
