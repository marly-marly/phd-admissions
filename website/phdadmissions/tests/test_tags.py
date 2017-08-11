import json

from tagging.models import Tag

from assets.constants import SUPERVISOR
from phdadmissions.models.application import Application
from phdadmissions.serializers.tag_serializer import TagSerializer
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import create_new_application, create_application_details
from authentication.tests.helper_functions import create_new_user, log_in


class TagsTestCase(BaseTestCase):
    # Tests if we can get/post/update/delete tags
    def test_get_post_update_delete_tags(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # New application
        create_new_application(token, create_application_details(self.academic_year.id, tags=['Ferrari', 'Porsche']),
                               self.client)

        # GET tags
        tags_response = self.client.get("/api/phd/admin/tags/", HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(tags_response.status_code, 200)
        response_content = json.loads(tags_response.content.decode('utf-8'))
        self.assertEqual(len(response_content["tags"]), 2)

        # POST duplicate tag
        new_tags_response = self.client.post("/api/phd/admin/tags/", {
            "name": 'Ferrari'
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_tags_response.status_code, 400)

        # POST good tag
        new_tags_response = self.client.post("/api/phd/admin/tags/", {
            "name": 'Lamborghini'
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_tags_response.status_code, 201)

        # UPDATE existing tag
        existing_tag = Tag.objects.filter(name="Lamborghini").first()
        existing_tag.name = "Lamborghini 02"
        tag_serializer = TagSerializer(existing_tag)
        update_tag_response = self.client.put(path="/api/phd/admin/tags/",
                                              data=json.dumps(
                                                  {"id": existing_tag.id, "tag": tag_serializer.data}),
                                              HTTP_AUTHORIZATION='JWT {}'.format(token),
                                              content_type='application/json')

        self.assertEqual(update_tag_response.status_code, 200)

        tags_response = self.client.get("/api/phd/admin/tags/", HTTP_AUTHORIZATION='JWT {}'.format(token))
        response_content = json.loads(tags_response.content.decode('utf-8'))
        existing_tag_names = [tag['name'] for tag in response_content["tags"]]
        self.assertIn("Lamborghini 02", existing_tag_names)

        # UPDATE duplicate tag
        existing_tag.name = "Ferrari"
        tag_serializer = TagSerializer(existing_tag)
        update_tag_response = self.client.put(path="/api/phd/admin/tags/",
                                              data=json.dumps(
                                                  {"id": existing_tag.id, "tag": tag_serializer.data}),
                                              HTTP_AUTHORIZATION='JWT {}'.format(token),
                                              content_type='application/json')

        self.assertEqual(update_tag_response.status_code, 400)

        # DELETE a tag
        delete_tag_response = self.client.delete(path="/api/phd/admin/tags/",
                                                 data=json.dumps({"id": existing_tag.id}),
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                 content_type='application/json')

        self.assertEqual(delete_tag_response.status_code, 204)
        existing_tag = Tag.objects.filter(name="Lamborghini 02").first()
        self.assertEqual(existing_tag, None)


class ApplicationTagsTestCase(BaseTestCase):
    # Tests if we can get/post/delete tags of existing applications
    def test_get_post_delete_tags_of_application(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # New applications
        create_new_application(token, create_application_details(self.academic_year.id, registry_ref="01",
                                                                 tags=['Ferrari', 'Porsche']),
                               self.client)
        create_new_application(token, create_application_details(self.academic_year.id, registry_ref="02",
                                                                 tags=['Lamborghini', 'Audi']),
                               self.client)
        create_new_application(token, create_application_details(self.academic_year.id, registry_ref="03",
                                                                 tags=['Ferrari', 'Audi']),
                               self.client)

        self.client.post("/api/phd/admin/tags/", {
            "name": "Tag with no application"
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        tags_response = self.client.get("/api/phd/application/tags/",
                                        HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(tags_response.status_code, 200)
        response_content = json.loads(tags_response.content.decode('utf-8'))
        self.assertEqual(len(response_content), 5)

        self.assertEqual(response_content['Ferrari']['count'], 2)
        self.assertEqual(response_content['Porsche']['count'], 1)
        self.assertEqual(response_content['Tag with no application']['count'], 0)

        # POST new tags
        existing_application = Application.objects.filter(registry_ref="01").first()
        self.client.post("/api/phd/application/tags/", {
            "application_id": existing_application.id,
            "name": "Toyota"
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        tags_response = self.client.get("/api/phd/application/tags/",
                                        HTTP_AUTHORIZATION='JWT {}'.format(token))

        response_content = json.loads(tags_response.content.decode('utf-8'))
        self.assertEqual(len(response_content), 6)

        self.assertEqual(response_content['Toyota']['count'], 1)

        # DELETE tag
        toyota_tag = Tag.objects.filter(name="Toyota").first()
        delete_tag_response = self.client.delete(path="/api/phd/application/tags/",
                                                 data=json.dumps({"tag_id": toyota_tag.id,
                                                                  "application_id": existing_application.id}),
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                 content_type='application/json')

        self.assertEqual(delete_tag_response.status_code, 204)

        tags_response = self.client.get("/api/phd/application/tags/",
                                        HTTP_AUTHORIZATION='JWT {}'.format(token))

        response_content = json.loads(tags_response.content.decode('utf-8'))
        self.assertEqual(len(response_content), 6)

        self.assertEqual(response_content['Toyota']['count'], 0)

    # Tests if we can get the top 5 supervisor counts per tag
    def test_get_recommended_supervisors(self):
        # Register supervisor
        create_new_user("Yeesha", "Woozles", user_type=SUPERVISOR)
        create_new_user("Pluto", "Woozles", user_type=SUPERVISOR)

        # Login as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        create_new_application(token, create_application_details(registry_ref="015243",
                                                                 academic_year_id=self.academic_year.id,
                                                                 supervisors=['Yeesha'],
                                                                 tags=['Porsche']), self.client)

        create_new_application(token, create_application_details(registry_ref="767575",
                                                                 academic_year_id=self.academic_year.id,
                                                                 supervisors=['Yeesha', 'Pluto'],
                                                                 tags=['Porsche', 'Ferrari']), self.client)

        recommended_supervisors_response = self.client.get(path="/api/phd/recommended_supervisors/",
                                                           data={'tags': ['Porsche', 'Ferrari']},
                                                           HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(recommended_supervisors_response.status_code, 200)
        response_content = json.loads(recommended_supervisors_response.content.decode('utf-8'))
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response_content[0]['total'], 2)
        self.assertEqual(response_content[0]['username'], 'Yeesha')
