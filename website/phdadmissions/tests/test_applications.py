from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
import json

from phdadmissions.models.application import Application


class ApplicationsTestCase(TestCase):

    client = Client()
    response = None

    def setUp(self):
        self.response = self.client.post("/api/auth/register/", {"username": "Heffalumps",
                                                                 "email": "heffalumps@woozles.com",
                                                                 "password": "Woozles",
                                                                 "user_type": "admin"})

    # Tests if the administrator can add a new application
    def test_new_phd_application(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # New
        new_application_response = self.client.post("/api/applications/add_or_edit/", {
            "new": False,
            "registry_ref": "012983234",
            "surname": "Szeles",
            "forename": "Marton",
            "possible_funding": "Self",
            "funding_status": "Pending",
            "origin": "EU",
            "student_type": "COMPUTING",
            "research_subject": "Investigating travelling at the speed of light."
        },HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_application_response.status_code, 201)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(latest_application.forename, "Marton")

        # Update
        new_application_response = self.client.post("/api/applications/add_or_edit/", {
            "new": True,
            "id": latest_application.id,
            "registry_ref": "012983234",
            "surname": "Szeles",
            "forename": "Martin",
            "possible_funding": "Self",
            "funding_status": "Pending",
            "origin": "EU",
            "student_type": "COMPUTING",
            "research_subject": "Investigating travelling at the speed of light."
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_application_response.status_code, 201)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(latest_application.forename, "Martin")
