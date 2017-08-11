from django.db.models import Count, Case, When, CharField
from django.db.models import F
from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from assets.constants import SUPERVISOR
from phdadmissions.models.application import Application


class RecommendedSupervisorsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns 5 recommended supervisors along with a count of their similar supervisions
    def get(self, request):
        tags = request.GET.getlist('tags')

        # Find the top 5 users who most frequently supervise an application that is associated with the given tags.
        # Admin supervisions count as 0 so that we can drop them after the query
        user_counts_per_tag = Application.tagged.with_any(tags=tags, queryset=None) \
            .annotate(username=F('supervisions__supervisor__username'),
                      first_name=F('supervisions__supervisor__first_name'),
                      last_name=F('supervisions__supervisor__last_name')) \
            .values('username', 'first_name', 'last_name', 'supervisions__type') \
            .annotate(total=Count(Case(When(supervisions__type=SUPERVISOR, then=1), output_field=CharField(),))) \
            .order_by('-total')[:5]

        # Drop admin supervisions from the result set
        supervisor_counts_per_tag = []
        for entry in user_counts_per_tag:
            if entry['supervisions__type'] == SUPERVISOR and entry['total'] > 0:
                supervisor_counts_per_tag.append(entry)

        json_response = JSONRenderer().render(supervisor_counts_per_tag)

        return HttpResponse(json_response, content_type='application/json')
