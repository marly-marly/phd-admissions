import json

from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.models.application import Application
from phdadmissions.serializers.academic_year_serializer import AcademicYearSerializer


class StatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns various statistics calculated from the application entities
    def get(self, request):
        current_academic_year = AcademicYear.objects.filter(default=True).first()
        if not current_academic_year:
            response_data = json.dumps({"error": "Please select a default academic year!", "current_academic_year": 0})
            return HttpResponseBadRequest(response_data, content_type='application/json')

        number_of_applications = Application.objects.filter(academic_year=current_academic_year).count()
        current_academic_year_json = AcademicYearSerializer(current_academic_year).data

        json_response = JSONRenderer().render(
            {"number_of_applications": number_of_applications, "current_academic_year": current_academic_year_json})

        return HttpResponse(json_response, content_type='application/json')