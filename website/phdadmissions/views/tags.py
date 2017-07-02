import json

from django.db import transaction
from django.http import HttpResponse
from django.db import IntegrityError
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import permissions

from tagging.models import Tag, TaggedItem

from phdadmissions.models.application import Application
from phdadmissions.serializers.tag_serializer import TagSerializer
from phdadmissions.utilities.custom_responses import throw_bad_request
from authentication.roles import roles


class TagsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Gets all tags from the database
    def get(self, request):

        tags = Tag.objects.all()
        tag_serializer = TagSerializer(tags, many=True)
        json_response = JSONRenderer().render({"tags": tag_serializer.data})

        return HttpResponse(json_response, content_type='application/json')

    # Uploads a new tag instance
    def post(self, request):
        data = request.data
        tag_name = data.get('name', None)

        try:
            with transaction.atomic():
                new_tag = Tag.objects.create(name=tag_name)
        except IntegrityError:
            return throw_bad_request("The tag '" + tag_name + "' already exists!")

        tag_serializer = TagSerializer(new_tag)
        json_response = JSONRenderer().render({"tag": tag_serializer.data})

        return HttpResponse(json_response, status=status.HTTP_201_CREATED, content_type='application/json')

    # Updates an existing tag instance
    def put(self, request):
        data = request.data
        id = data.get('id', None)
        existing_tag = Tag.objects.filter(id=id).first()
        if not existing_tag:
            return throw_bad_request("No tag exists with the ID: " + str(id))

        tag = data.get('tag', None)
        existing_tag.name = tag['name']
        try:
            with transaction.atomic():
                existing_tag.save()
        except IntegrityError:
            return throw_bad_request("The tag '" + tag['name'] + "' already exists!")

        return HttpResponse(status=status.HTTP_200_OK)

    # Deletes an existing tag
    def delete(self, request):
        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        request_body = request.body.decode('utf-8')
        data = json.loads(request_body)
        id = data.get('id')

        if not id:
            return throw_bad_request("Tag id was not provided as a GET parameter.")

        tag = Tag.objects.filter(id=id).first()
        if not tag:
            return throw_bad_request("Tag was not find with the ID." + str(id))

        tag.delete()

        return HttpResponse(status=204)


class ApplicationTagsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    # Returns all tags with their counts on applications
    def get(self, request):
        all_tags = Tag.objects.all()
        application_tags = Tag.objects.usage_for_model(Application, counts=True)

        tag_count_map = {}
        for tag in all_tags:
            tag_count_map[tag.name] = {
                'id': tag.id,
                'count': 0
            }

        for tag in application_tags:
            tag_count_map[tag.name]['count'] = tag.count

        json_response = json.dumps(tag_count_map)

        return HttpResponse(json_response, content_type='application/json')

    # Adds new tags to an existing application
    def post(self, request):
        data = request.data
        tag_name = data.get('name', None)
        application_id = data.get('application_id', None)

        application = Application.objects.filter(id=application_id).first()
        if not application:
            return throw_bad_request("Application could not be found with the id: " + str(application_id))

        Tag.objects.add_tag(application, "\"" + tag_name + "\"")
        tag = Tag.objects.filter(name=tag_name).first()

        # Return the tag object
        tag_serializer = TagSerializer(tag)
        json_response = JSONRenderer().render({"tag": tag_serializer.data})

        return HttpResponse(json_response, content_type='application/json')

    # Deletes an existing tag from an application
    def delete(self, request):
        user = request.user
        if user.role != roles.ADMIN:
            return throw_bad_request("No sufficient permission.")

        request_body = request.body.decode('utf-8')
        data = json.loads(request_body)
        tag_id = data.get('tag_id')

        if not tag_id:
            return throw_bad_request("Tag ID was not provided as a GET parameter.")

        application_id = data.get('application_id')

        if not application_id:
            return throw_bad_request("Application ID was not provided as a GET parameter.")

        tagged_item = TaggedItem.objects.filter(object_id=application_id, tag_id=tag_id).first()
        if not tagged_item:
            return throw_bad_request("Unable to delete tag from application: the application does not have this tag.")

        tagged_item.delete()

        return HttpResponse(status=204)