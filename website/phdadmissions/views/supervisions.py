import json

from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from assets.constants import ADMIN, SUPERVISOR
from authentication.roles import roles
from phdadmissions.models.application import Application, application_updated_now
from phdadmissions.models.supervision import Supervision
from phdadmissions.serializers.supervision_serializer import SupervisionSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request, throw_invalid_data


class SupervisionView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Adds a new supervision to a specific application
    def post(self, request):

        data = request.data
        supervision_type_param = data.get('supervision_type', None)
        if supervision_type_param and supervision_type_param == ADMIN:
            user = request.user
            if user.role != roles.ADMIN:
                return throw_bad_request("No sufficient permission.")
            supervision_type = ADMIN
        else:
            supervision_type = SUPERVISOR

        application_id = data.get('id', None)
        application = Application.objects.filter(id=application_id).first()
        if not application:
            return throw_bad_request("Application was not found with the id: " + str(application_id))

        supervisor_username = data.get('supervisor', None)
        supervisor = User.objects.filter(username=supervisor_username).first()
        if not supervisor:
            return throw_bad_request("Supervisor was not find with the username: " + str(supervisor_username))

        try:
            with transaction.atomic():
                new_supervision = Supervision.objects.create(application=application, supervisor=supervisor,
                                                             type=supervision_type)
        except IntegrityError:
            return throw_bad_request("The " + supervision_type + "supervision already exists!")

        application_updated_now(application)

        supervision_serializer = SupervisionSerializer(new_supervision)
        json_response = JSONRenderer().render(supervision_serializer.data)

        return HttpResponse(json_response, content_type='application/json')

    # Removes a supervision from a specific application
    def delete(self, request):
        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = json.loads(request.body.decode('utf-8'))

        supervision_id = data.get('supervision_id')
        if not supervision_id:
            return throw_bad_request("No supervision was specified.")

        supervision = Supervision.objects.filter(id=supervision_id).first()
        if not supervision:
            return throw_bad_request("Supervision could not be found with the id: " + str(supervision_id))

        if not supervision.creator:
            supervision.delete()
        else:
            return throw_bad_request("Cannot delete creator supervision.")

        return HttpResponse(status=204)

    # Updates an existing Supervision instance
    def put(self, request):
        data = request.data
        supervision_id = data.get('supervision_id', None)

        if not supervision_id:
            return throw_bad_request("No supervision was specified.")

        supervision = Supervision.objects.filter(id=supervision_id).first()
        if not supervision:
            return throw_bad_request("Supervision could not be found with the id " + str(supervision_id))

        # TODO check user roles here
        supervision_serializer = SupervisionSerializer(instance=supervision, data=data["supervision"], partial=True)
        if not supervision_serializer.is_valid():
            return throw_invalid_data(supervision_serializer.errors)
        supervision_serializer.save()
        application_updated_now(supervision.application)

        return Response(status=status.HTTP_200_OK)


class SupervisionAllocationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Sets the allocation flag of a supervision to be true
    def post(self, request):
        if request.user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = request.data
        supervision_id = data.get('supervision_id', None)
        if supervision_id is None:
            throw_bad_request("No supervision ID was specified.")

        supervision = Supervision.objects.filter(id=supervision_id).first()
        if not supervision:
            return throw_bad_request("Supervision was not found with the ID: " + str(supervision_id))

        supervision.allocated = True
        supervision.save()

        return HttpResponse(status=status.HTTP_200_OK)

    # Sets the allocation flag of a supervision to be false
    def delete(self, request):
        if request.user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        data = json.loads(request.body.decode('utf-8'))

        supervision_id = data.get('supervision_id')
        if not supervision_id:
            return throw_bad_request("No supervision was specified.")

        supervision = Supervision.objects.filter(id=supervision_id).first()
        if not supervision:
            return throw_bad_request("Supervision could not be found with the id: " + str(supervision_id))

        supervision.allocated = False
        supervision.save()

        return HttpResponse(status=status.HTTP_200_OK)
