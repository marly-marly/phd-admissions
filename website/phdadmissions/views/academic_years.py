import json

from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from authentication.roles import roles
from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.serializers.academic_year_serializer import AcademicYearSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request, throw_invalid_data


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
            return throw_invalid_data(academic_year_serializer.errors)

        academic_year = academic_year_serializer.save()
        academic_year_serializer = AcademicYearSerializer(academic_year)
        json_response = JSONRenderer().render({"academic_year": academic_year_serializer.data})

        return HttpResponse(json_response, status=status.HTTP_201_CREATED, content_type='application/json')

    # Updates an existing academic year in the database
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
            return throw_invalid_data(academic_year_serializer.errors)

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