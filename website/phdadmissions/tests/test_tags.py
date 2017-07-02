import json

from tagging.models import Tag

from phdadmissions.serializers.tag_serializer import TagSerializer
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import log_in, create_new_application, create_application_details


class TagsTestCase(BaseTestCase):
    # Tests if we can get/post/update/delete tags
    def test_get_post_update_delete_tags(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # New application
        create_new_application(token, create_application_details(self.academic_year.id, tags=['Ferrari', 'Porsche']),
                               self.client)

        # GET tags
        tags_response = self.client.get("/api/applications/admin/tags/", HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(tags_response.status_code, 200)
        response_content = json.loads(tags_response.content.decode('utf-8'))
        self.assertEqual(len(response_content["tags"]), 2)

        # POST duplicate tag
        new_tags_response = self.client.post("/api/applications/admin/tags/", {
            "name": 'Ferrari'
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_tags_response.status_code, 400)

        # POST good tag
        new_tags_response = self.client.post("/api/applications/admin/tags/", {
            "name": 'Lamborghini'
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_tags_response.status_code, 201)

        # UPDATE existing tag
        existing_tag = Tag.objects.filter(name="Lamborghini").first()
        existing_tag.name = "Lamborghini 02"
        tag_serializer = TagSerializer(existing_tag)
        update_tag_response = self.client.put(path="/api/applications/admin/tags/",
                                              data=json.dumps(
                                                  {"id": existing_tag.id, "tag": tag_serializer.data}),
                                              HTTP_AUTHORIZATION='JWT {}'.format(token),
                                              content_type='application/json')

        self.assertEqual(update_tag_response.status_code, 200)

        tags_response = self.client.get("/api/applications/admin/tags/", HTTP_AUTHORIZATION='JWT {}'.format(token))
        response_content = json.loads(tags_response.content.decode('utf-8'))
        existing_tag_names = [tag['name'] for tag in response_content["tags"]]
        self.assertIn("Lamborghini 02", existing_tag_names)

        # UPDATE duplicate tag
        existing_tag.name = "Ferrari"
        tag_serializer = TagSerializer(existing_tag)
        update_tag_response = self.client.put(path="/api/applications/admin/tags/",
                                              data=json.dumps(
                                                  {"id": existing_tag.id, "tag": tag_serializer.data}),
                                              HTTP_AUTHORIZATION='JWT {}'.format(token),
                                              content_type='application/json')

        self.assertEqual(update_tag_response.status_code, 400)

        # DELETE a tag
        delete_tag_response = self.client.delete(path="/api/applications/admin/tags/",
                                                 data=json.dumps({"id": existing_tag.id}),
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                 content_type='application/json')

        self.assertEqual(delete_tag_response.status_code, 204)
        existing_tag = Tag.objects.filter(name="Lamborghini 02").first()
        self.assertEqual(existing_tag, None)
