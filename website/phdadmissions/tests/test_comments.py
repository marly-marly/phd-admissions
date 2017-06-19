from django.test import TestCase
from django.test import Client
import json
from assets.constants import *
from django.utils import timezone

from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.models.application import Application
from phdadmissions.tests.helper_functions import create_new_application, create_application_details


class CommentsTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):
        self.response = self.client.post("/api/auth/register/", {"username": "Heffalumps",
                                                                 "email": "heffalumps@woozles.com",
                                                                 "password": "Woozles"})

        # New academic year
        self.academic_year = AcademicYear.objects.create(name="17/18", start_date=timezone.now(),
                                                         end_date=timezone.now(), default=True)

    # Tests if a supervisor can add a new comment
    def test_add_new_comment(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # Register a supervisor
        supervisor_response = self.client.post("/api/auth/register/", {"username": "Atrus1",
                                                                       "email": "atrus1@woozles.com",
                                                                       "password": "Woozles",
                                                                       "user_type": "SUPERVISOR"})

        # New application
        create_new_application(token, create_application_details(self.academic_year.id), self.client)
        latest_application = Application.objects.latest(field_name="created_at")

        # Add supervision
        self.client.post("/api/applications/supervision/", {
            "id": latest_application.id,
            "supervisor": "Atrus1"
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        latest_application = Application.objects.latest(field_name="created_at")
        supervisions = latest_application.supervisions.filter(type=SUPERVISOR)
        supervision = supervisions[0]
        self.assertEqual(len(supervision.comments.all()), 0)

        # Post the new comment as the appropriate supervisor
        response_content = json.loads(supervisor_response.content.decode('utf-8'))
        token = response_content["token"]

        new_comment_response = self.client.post("/api/applications/comment/", {
            "supervision_id": supervision.id,
            "content": "This application is awesome!",
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_comment_response.status_code, 200)
        self.assertEqual(len(supervision.comments.all()), 1)

        # Update
        put_data = json.dumps({
            "supervision_id": supervision.id,
            "supervision": {
                "acceptance_condition": "Only if you get an A.",
                "recommendation": OTHER_RECOMMEND
            }})
        self.client.put("/api/applications/supervision/", data=put_data, HTTP_AUTHORIZATION='JWT {}'.format(token),
                        content_type='application/json')

        supervisions = latest_application.supervisions.filter(type=SUPERVISOR)
        supervision = supervisions[0]
        self.assertEqual(supervision.recommendation, OTHER_RECOMMEND)

    # Tests if aan admin can comment under an application without a supervision initially
    def test_add_new_comment_as_admin(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # New application
        create_new_application(token, create_application_details(self.academic_year.id), self.client)
        latest_application = Application.objects.latest(field_name="created_at")

        # Register a new admin
        response = self.client.post("/api/auth/register/", {"username": "Atrus",
                                                            "email": "atrus@woozles.com",
                                                            "password": "Atruuus"})
        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # Add comment
        new_comment_response = self.client.post("/api/applications/comment/", {
            "application_id": latest_application.id,
            "content": "This application is awesome!",
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_comment_response.status_code, 200)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(len(latest_application.supervisions.all()), 2)
