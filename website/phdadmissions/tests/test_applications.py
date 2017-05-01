from django.test import TestCase
from django.test import Client
import json
from assets.constants import *

from phdadmissions.models.application import Application


class ApplicationsTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):
        self.response = self.client.post("/api/auth/register/", {"username": "Heffalumps",
                                                                 "email": "heffalumps@woozles.com",
                                                                 "password": "Woozles",
                                                                 "user_type": "ADMIN"})

    # Tests if the administrator can add a new application, and if we can get the data as well
    def test_new_phd_application(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # Register two supervisors
        self.client.post("/api/auth/register/", {"username": "Atrus1",
                                                 "email": "atrus1@woozles.com",
                                                 "password": "Woozles",
                                                 "user_type": "SUPERVISOR"})

        self.client.post("/api/auth/register/", {"username": "Atrus2",
                                                 "email": "atrus2@woozles.com",
                                                 "password": "Woozles",
                                                 "user_type": "SUPERVISOR"})

        # New
        post_data = json.dumps({"new": True,
                                "registry_ref": "012983234",
                                "surname": "Szeles",
                                "forename": "Marton",
                                "possible_funding": "SELF",
                                "funding_status": "PENDING",
                                "origin": "EU",
                                "student_type": "COMPUTING",
                                "supervisors": ["Atrus1", "Atrus2"],
                                "research_subject": "Investigating travelling at the speed of light.",
                                "registry_comment": None})

        new_application_response = self.client.post(path="/api/applications/application/", data=post_data,
                                                    HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                    content_type='application/json')

        self.assertEqual(new_application_response.status_code, 201)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(latest_application.forename, "Marton")
        self.assertEqual(latest_application.status, PENDING_STATUS)
        self.assertEqual(latest_application.registry_comment, None)
        self.assertEqual(len(latest_application.supervisions.all()), 2)

        # Update
        post_data = json.dumps({"new": False,
                                "id": latest_application.id,
                                "registry_ref": "9874334",
                                "surname": "Szeles",
                                "forename": "Martin",
                                "possible_funding": "SELF",
                                "funding_status": "PENDING",
                                "origin": "EU",
                                "student_type": "COMPUTING",
                                "supervisors": ["Atrus1", "Atrus2"],
                                "status": "PENDING",
                                "research_subject": "Investigating travelling at the speed of light.",
                                "registry_comment": "Awesome"})

        new_application_response = self.client.post(path="/api/applications/application/", data=post_data,
                                                    HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                    content_type='application/json')

        self.assertEqual(new_application_response.status_code, 201)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(latest_application.forename, "Martin")
        self.assertEqual(latest_application.registry_comment, "Awesome")

        # Check if we can read the data through the endpoint
        search_result_response = self.client.get("/api/applications/application/", {"id": latest_application.id},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))
        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        application = search_result_response_content["application"]
        self.assertEqual(application["forename"], "Martin")
        self.assertEqual(len(application["supervisions"]), 2)

    # Tests if the administrator can add or delete a supervision corresponding to an application
    def test_add_and_delete_supervision(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # Register a supervisor
        self.client.post("/api/auth/register/", {"username": "Atrus1",
                                                 "email": "atrus1@woozles.com",
                                                 "password": "Woozles",
                                                 "user_type": "SUPERVISOR"})

        # New
        post_data = json.dumps({
            "new": True,
            "registry_ref": "012983234",
            "surname": "Szeles",
            "forename": "Marton",
            "possible_funding": "SELF",
            "funding_status": "PENDING",
            "origin": "EU",
            "student_type": "COMPUTING",
            "supervisors": [],
            "research_subject": "Investigating travelling at the speed of light.",
            "registry_comment": "Awesome"
        })
        self.client.post(path="/api/applications/application/", data=post_data,
                         HTTP_AUTHORIZATION='JWT {}'.format(token), content_type='application/json')

        latest_application = Application.objects.latest(field_name="created_at")

        # Add
        new_supervision_response = self.client.post("/api/applications/supervision/", {
            "action": "ADD",
            "id": latest_application.id,
            "supervisor": "Atrus1"
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_supervision_response.status_code, 200)

        latest_application = Application.objects.latest(field_name="created_at")
        supervisions = latest_application.supervisions.all()
        self.assertEqual(len(supervisions), 1)

        # Delete
        self.client.post("/api/applications/supervision/", {
            "action": "DELETE",
            "id": latest_application.id,
            "supervisor": "Atrus1",
            "supervision_id": supervisions[0].id
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        latest_application = Application.objects.latest(field_name="created_at")
        supervisions = latest_application.supervisions.all()
        self.assertEqual(len(supervisions), 0)

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

        # New
        post_data = json.dumps({
            "new": True,
            "registry_ref": "012983234",
            "surname": "Szeles",
            "forename": "Marton",
            "possible_funding": "SELF",
            "funding_status": "PENDING",
            "origin": "EU",
            "student_type": "COMPUTING",
            "supervisors": [],
            "research_subject": "Investigating travelling at the speed of light.",
            "registry_comment": None
        })
        self.client.post(path="/api/applications/application/", data=post_data,
                         HTTP_AUTHORIZATION='JWT {}'.format(token), content_type='application/json')

        latest_application = Application.objects.latest(field_name="created_at")

        # Add
        self.client.post("/api/applications/supervision/", {
            "action": "ADD",
            "id": latest_application.id,
            "supervisor": "Atrus1"
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        latest_application = Application.objects.latest(field_name="created_at")
        supervisions = latest_application.supervisions.all()
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

    # Tests if we can search for applications
    def test_application_search(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # New application
        post_data = json.dumps({
            "new": True,
            "registry_ref": "012983234",
            "surname": "Szeles",
            "forename": "Marton",
            "possible_funding": "SELF",
            "funding_status": "PENDING",
            "origin": "EU",
            "student_type": "COMPUTING",
            "supervisors": [],
            "research_subject": "Investigating travelling at the speed of light.",
            "registry_comment": None
        })

        self.client.post(path="/api/applications/application/", data=post_data,
                         HTTP_AUTHORIZATION='JWT {}'.format(token),
                         content_type='application/json')

        post_data = json.dumps({
            "new": True,
            "registry_ref": "7374636",
            "surname": "Atrus",
            "forename": "Yeesha",
            "possible_funding": "SELF",
            "funding_status": "PENDING",
            "origin": "OVERSEAS",
            "student_type": "COMPUTING_AND_CDT",
            "supervisors": [],
            "research_subject": "Investigating writing linking books.",
            "registry_comment": None
        })
        self.client.post(path="/api/applications/application/", data=post_data,
                         HTTP_AUTHORIZATION='JWT {}'.format(token), content_type='application/json')

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"surname": "Szeles"},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 1)

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"forename": "a"},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 2)

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"forename": "a", "origin": "EU"},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 1)

    # Tests if we can get the list of choices for the application form
    def test_get_application_choices(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        choices_response = self.client.get(path="/api/applications/choices/application/", data={}, HTTP_AUTHORIZATION='JWT {}'.format(token))

        choices_response_content = json.loads(choices_response.content.decode('utf-8'))
        self.assertEqual(len(choices_response_content["possible_funding"]), 7)
