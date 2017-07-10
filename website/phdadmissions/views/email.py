from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from assets.constants import EMAIL
from authentication.roles import roles
from phdadmissions.models.configuration import Configuration
from phdadmissions.serializers.configuration_serializer import ConfigurationSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request


class EmailConfigurationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns the email configuration
    def get(self, request):

        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        email_configuration = Configuration.objects.filter(name=EMAIL).first()
        if email_configuration is None:
            email_configuration = Configuration.objects.create(name=EMAIL, value="")

        email_configuration_serializer = ConfigurationSerializer(email_configuration)
        json_response = JSONRenderer().render(email_configuration_serializer.data)

        return HttpResponse(json_response, content_type='application/json')

    # Updates the email configuration
    def put(self, request):

        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        email_configuration = Configuration.objects.filter(name=EMAIL).first()
        if email_configuration is None:
            return throw_bad_request("No email configuration exists yet.")

        data = request.data
        value = data.get('value', None)
        email_configuration_serializer = ConfigurationSerializer(instance=email_configuration, data={'value': value},
                                                                 partial=True)
        if not email_configuration_serializer.is_valid():
            return throw_bad_request("Posted data was invalid.")

        email_configuration_serializer.save()

        return Response(status=status.HTTP_200_OK)
