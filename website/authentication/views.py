import json

from django.contrib.auth import logout, authenticate
from django.contrib.auth.models import User, update_last_login
from django.core.management import call_command
from django.http import QueryDict
from django.http.response import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings

from assets.constants import SUPERVISOR
from assets.settings import USER_ROLES
from authentication.serializers import AccountSerializer
from authentication.models import UserRole
from phdadmissions.utilities.custom_responses import throw_bad_request


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    # Returns the authentication token, username, and user-role
    def post(self, request):
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        try:
            user = authenticate(username=username, password=password)
        except MultiValueDictKeyError:
            return throw_bad_request("Missing username or password")

        if user is None:
            return throw_bad_request("Wrong username or password")

        if user.is_active:

            # If this is the first time the user logged in, assign a default role
            if hasattr(user, 'role'):
                user_role = user.role
            else:
                user_role = UserRole.objects.create(name=SUPERVISOR, user=user)

            # Manually generate a token for the new user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            update_last_login(None, user)

            return Response({
                'token': token,
                'username': user.username,
                'user_role': user_role.name
            })
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'This account has been disabled.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class RestrictedView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):

        # If the user can access this view, that means the user is authenticated
        response_data = json.dumps({"authenticated": True})
        return HttpResponse(response_data, content_type='application/json')


class StaffView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns all staff members along with their user roles
    def get(self, request):
        users = User.objects.all().prefetch_related('role').order_by('last_name', 'first_name')
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

        return HttpResponse(status=status.HTTP_200_OK)


class StaffSynchronisationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Synchronises the list of DoC staff members with the User table
    def post(self, request):
        if request.user.role.name == SUPERVISOR:
            return throw_bad_request("You have no permission to synchronise staff members.")

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


