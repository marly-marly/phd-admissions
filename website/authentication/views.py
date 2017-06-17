import json

from django.contrib.auth import logout
from django.contrib.auth.models import User, update_last_login
from django.http import QueryDict
from django.http.response import HttpResponse
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings

from authentication.serializers import AccountSerializer
from authentication.models import UserRole


class RegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):

        # Read basic required parameters
        data = request.data
        username = data.get('username', None)
        password = data.get('password', None)
        account_data = {'username': username, 'password': password, }
        account_data_qd = QueryDict('', mutable=True)
        account_data_qd.update(account_data)
        serializer = AccountSerializer(data=account_data_qd)

        if serializer.is_valid():

            # Create the user entity and add its role
            user = User.objects.create_user(**serializer.validated_data)
            user_type = data.get('user_type', None)
            if user_type is None:
                user_type = "ADMIN"
            UserRole.objects.create(name=user_type, user=user)

            # Manually generate a token for the new user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            update_last_login(None, user)

            response_dictionary = {
                'token': token,
                'username': user.username,
                'user_role': user.role.name
            }

            return Response(response_dictionary, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'Bad request',
            'message': 'Account could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                if user.is_active:

                    # Manually generate a token for the new user
                    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)

                    update_last_login(None, user)

                    return Response({
                        'token': token,
                        'username': user.username,
                        'user_role': user.role.name
                    })
                else:
                    return Response({
                        'status': 'Unauthorized',
                        'message': 'This account has been disabled.'
                    }, status=status.HTTP_401_UNAUTHORIZED)

            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'Username/password combination invalid.'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username/password combination invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)


class RestrictedView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request):

        # If the user can access this view, that means the user is authenticated
        response_data = json.dumps({"authenticated": True})
        return HttpResponse(response_data, content_type='application/json')
