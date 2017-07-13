from django.core.management import call_command
from django.db.models import F
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import permissions
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, CharField

from assets.constants import SUPERVISOR
from assets.settings import USER_ROLES
from authentication.serializers import AccountSerializer
from phdadmissions.models.application import Application
from phdadmissions.utilities.custom_responses import throw_bad_request


class StaffView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns all staff members along with their user roles
    def get(self, request):
        users = User.objects.all()
        account_serializer = AccountSerializer(users, many=True)
        json_response = JSONRenderer().render(account_serializer.data)

        return HttpResponse(json_response, content_type='application/json')


class SupervisorStaffView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns all supervisor staff members along with their user roles
    def get(self, request):
        users = User.objects.filter(role__name=SUPERVISOR).values('first_name', 'last_name', 'username').order_by(
            'last_name', 'first_name')
        account_serializer = AccountSerializer(users, many=True)
        json_response = JSONRenderer().render(account_serializer.data)

        return HttpResponse(json_response, content_type='application/json')


class StaffRoleView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Changes the user role of the specified staff members
    def post(self, request):
        requesting_user = request.user
        requesting_user_role = requesting_user.role
        if requesting_user_role.name == SUPERVISOR:
            return throw_bad_request("You have no permission to change users' roles.")

        data = request.data
        new_user_roles = data.get('new_user_roles', None)
        if not new_user_roles:
            return throw_bad_request("No users were specified.")

        for user, role in new_user_roles.items():
            user_object = User.objects.filter(username=user).first()
            if not user_object:
                return throw_bad_request("No user was found with the ID " + str(user))

            if role not in USER_ROLES:
                return throw_bad_request("The following roles was invalid: " + str(role))

            current_user_role = user_object.role
            current_user_role.name = role
            current_user_role.save()

        json_response = JSONRenderer().render({"success": True})

        return HttpResponse(json_response, content_type='application/json')


class StaffSynchronisationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Synchronises the list of DoC staff members with the User table
    def post(self, request):
        call_command('ldap_sync_users')

        return HttpResponse(status=HTTP_200_OK, content_type='application/json')


class SupervisorView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns the list of supervisor usernames
    def get(self, request):
        usernames = User.objects.filter(role__name=SUPERVISOR).values_list('username', flat=True)

        json_response = JSONRenderer().render({"usernames": usernames})

        return HttpResponse(json_response, content_type='application/json')


class RecommendedSupervisorsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns the list of supervisor usernames
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
