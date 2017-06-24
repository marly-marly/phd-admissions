from django.core.management import call_command
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import permissions
from django.contrib.auth.models import User

from assets.constants import SUPERVISOR
from assets.settings import USER_ROLES, LDAP_AUTH_CONNECTION_USERNAME, LDAP_AUTH_CONNECTION_PASSWORD, LDAP_AUTH_URL
from authentication.serializers import AccountSerializer
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
            'first_name', 'last_name')
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
