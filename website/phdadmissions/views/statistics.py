import json
from itertools import groupby
from operator import itemgetter

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from assets.constants import SUPERVISOR
from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.models.application import Application
from phdadmissions.models.supervision import Supervision
from phdadmissions.serializers.academic_year_serializer import AcademicYearSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request
from datetime import datetime, timedelta, time
from django.utils import timezone


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
        number_of_allocated_supervisions = Application.objects.filter(supervisions__allocated=True).count()
        current_academic_year_json = AcademicYearSerializer(current_academic_year).data

        json_response = JSONRenderer().render(
            {"number_of_applications": number_of_applications,
             "number_of_allocated_supervisions": number_of_allocated_supervisions,
             "current_academic_year": current_academic_year_json})

        return HttpResponse(json_response, content_type='application/json')


class RatioStatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns statistics of various application ratios
    def get(self, request):
        academic_year_id = request.GET.get('academic_year_id', None)
        if academic_year_id is None:
            default_academic_year = AcademicYear.objects.filter(default=True).first()
            if default_academic_year is None:
                return throw_bad_request("No default academic year exists!")

            academic_year_id = default_academic_year.id

        fields = request.GET.getlist('fields')
        ratios = {}

        if academic_year_id == "all":
            applications = Application.objects.all()
        else:
            applications = Application.objects.filter(academic_year_id=academic_year_id)

        for field in fields:
            field_counts = applications.values(field).annotate(field_count=Count(field))
            field_series = [entry[field] for entry in field_counts]
            field_labels = [entry[field] for entry in field_counts]
            field_data = [entry['field_count'] for entry in field_counts]

            ratios[field] = {'series': field_series,
                             'labels': field_labels,
                             'data': field_data}

        json_response = JSONRenderer().render(ratios)

        return HttpResponse(json_response, content_type='application/json')


class StaffStatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns various statistics calculated from staff members' activity
    def get(self, request):
        # Number of users active today
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        number_of_users_today = User.objects.filter(last_login__lte=today_end, last_login__gte=today_start).count()

        # Average number of supervisions per supervisor
        supervision_counts = Supervision.objects.filter(type=SUPERVISOR).values('supervisor_id').annotate(
            supervision_count=Count('id'))
        average_supervisions = sum(
            [supervision_count['supervision_count'] for supervision_count in supervision_counts]) / len(
            supervision_counts)

        json_response = JSONRenderer().render({"number_of_users_today": number_of_users_today,
                                               "average_supervisions_per_supervisor": average_supervisions})

        return HttpResponse(json_response, content_type='application/json')


class ApplicationStatisticsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns various statistics calculated from applications in the database
    def get(self, request):

        academic_year_id = request.GET.get('academic_year_id', None)
        if academic_year_id is None:
            default_academic_year = AcademicYear.objects.filter(default=True).first()
            if default_academic_year is None:
                return throw_bad_request("No default academic year exists!")

            academic_year_id = default_academic_year.id

        if academic_year_id == "all":
            applications = Application.objects.all()
        else:
            applications = Application.objects.filter(academic_year_id=academic_year_id)

        applications_per_day = applications.filter().extra(select={'day': 'date( created_at )'}).values(
            'day').annotate(available=Count('id'))

        applications_per_day = list(applications_per_day)

        # Filling in the gaps for missing days
        dates = [application['day'] for application in applications_per_day]
        for day in (datetime.now().date() - timedelta(days=x) for x in range(0, 30)):
            if day not in dates:
                applications_per_day.append({'day': day, 'available': 0})

        sorted_applications_per_date = sorted(applications_per_day, key=itemgetter('day'))
        sorted_applications_per_day = []

        # Group by the dates
        for key, values in groupby(sorted_applications_per_date, key=lambda row: row['day']):
            sum = 0
            for value in values:
                sum += value['available']

                sorted_applications_per_day.append({'day': key, 'available': sum})

        applications_per_day_labels = []
        applications_per_day_data = []
        for entry in sorted_applications_per_day:
            applications_per_day_labels.append(entry['day'])
            applications_per_day_data.append(entry['available'])
        applications_per_day_series = ["Number of Applications"]

        json_response = JSONRenderer().render({"applications_by_day": {
            "labels": applications_per_day_labels,
            "data": applications_per_day_data,
            "series": applications_per_day_series
        }})

        return HttpResponse(json_response, content_type='application/json')
