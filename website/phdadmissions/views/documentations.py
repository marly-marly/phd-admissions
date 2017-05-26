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
from assets.settings import MEDIA_URL

from phdadmissions.models.application import Application
from phdadmissions.models.documentation import Documentation, SUB_FOLDER
from phdadmissions.models.supervision import Supervision
from phdadmissions.serializers.documentation_serializer import DocumentationSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request


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

        application_ids = request.GET.getlist('application_ids')
        applications = Application.objects.filter(id__in=application_ids)

        # Open StringIO to grab in-memory ZIP contents
        bytes_io = BytesIO()

        # The zip compressor
        zf = zipfile.ZipFile(bytes_io, "w")

        for application in applications.all():
            for supervision in application.supervisions.all():
                for documentation in supervision.documentations.all():

                    # Path within the ZIP
                    zip_path = documentation.file.url
                    cropped_zip_path = zip_path.replace(MEDIA_URL + SUB_FOLDER, "", 1)

                    # Add file, at correct path
                    zf.write(documentation.file.path, cropped_zip_path)

        # Must close zip for all contents to be written
        zf.close()

        # Grab ZIP file from in-memory, make response with correct MIME-type
        response = HttpResponse(bytes_io.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename=%s' % "Application Files.zip"

        return response
