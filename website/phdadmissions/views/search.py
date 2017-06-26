import json
import operator
from functools import reduce

from django.db.models import Q
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import permissions
from tagging.models import TaggedItem

from phdadmissions.models.application import Application, disjunction_applications_by_possible_funding
from phdadmissions.serializers.application_serializer import ApplicationSerializer


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

        supervised_by = request.GET.get('supervised_by', None)
        creator = request.GET.get('creator', None)
        supervision_type = request.GET.get('supervision_type', None)
        allocated = request.GET.get('allocated', None)

        tags = request.GET.getlist('tags')

        applications = Application.objects.filter(registry_ref__icontains=registry_ref, surname__icontains=surname,
                                                  forename__icontains=forename).prefetch_related("supervisions",
                                                                                                 "supervisions__supervisor",
                                                                                                 "supervisions__comments",
                                                                                                 "supervisions__documentations")
        if academic_year_name is not None:
            applications = applications.filter(academic_year__name=academic_year_name)

        if len(application_status) > 0:
            applications = applications.filter(status__in=application_status)

        if len(possible_funding) > 0:
            applications = disjunction_applications_by_possible_funding(applications, possible_funding)

        if len(funding_status) > 0:
            applications = applications.filter(funding_status__in=funding_status)

        if len(origin) > 0:
            applications = applications.filter(origin__in=origin)

        if len(student_type) > 0:
            applications = applications.filter(student_type__in=student_type)

        if len(tags) > 0:
            applications = TaggedItem.objects.get_by_model(Application, tags)

        # Filter the corresponding supervision relations
        filter_clauses = []

        if supervised_by is not None:
            filter_clauses.append(Q(supervisions__supervisor__username=supervised_by))

        if creator is not None:
            filter_clauses.append(Q(supervisions__creator=creator))

        if supervision_type is not None:
            filter_clauses.append(Q(supervisions__type=supervision_type))

        if allocated is not None:
            allocated = json.loads(allocated)
            filter_clauses.append(Q(supervisions__allocated=allocated))

        # AND the supervision clauses together since they should related to the same supervision instance
        if len(filter_clauses) > 0:
            applications = applications.filter(reduce(operator.and_, filter_clauses))

        application_serializer = ApplicationSerializer(applications, many=True)
        json_response = JSONRenderer().render({"applications": application_serializer.data})

        return HttpResponse(json_response, content_type='application/json')