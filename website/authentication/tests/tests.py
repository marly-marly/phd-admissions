from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
import json

from assets.constants import SUPERVISOR, ADMIN
from authentication.models import UserRole
from authentication.tests.helper_functions import create_new_user, log_in


class AuthenticationViewTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):
        user = User.objects.create_user(username="Heffalumps", email="heffalumps@woozles.com", password="Woozles")
        UserRole.objects.create(name=SUPERVISOR, user=user)

    # This test case will also attempt to use LDAP, which takes about 10 seconds, so it is commented out.
    # def test_unauthorised_access(self):
    #     response = self.client.post("/api/auth/get_token/", {"username": "Mango", "password": "Apple"})
    #     self.assertEqual(response.status_code, 400, "There shouldn't be a token received.")
    #
    #     response = self.client.post("/api/auth/authenticated/", {}, HTTP_AUTHORIZATION='JWT {}'.format("bad token"))
    #     self.assertEqual(response.status_code, 401, "There shouldn't be access granted.")

    def test_authorised_access(self):
        response = self.client.post("/api/auth/get_token/", {"username": "Heffalumps", "password": "Woozles"})
        self.assertEqual(response.status_code, 200, "The token should be successfully returned.")

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        response = self.client.post("/api/auth/authenticated/", {}, HTTP_AUTHORIZATION='JWT {}'.format(token))
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertTrue(response_content["authenticated"], "The user should be able to access this endpoint.")

    def test_authorised_access_via_login(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})
        self.assertEqual(response.status_code, 200, "The token should be successfully returned.")

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        response = self.client.post("/api/auth/authenticated/", {}, HTTP_AUTHORIZATION='JWT {}'.format(token))
        response_content = json.loads(response.content.decode('utf-8'))

        self.assertTrue(response_content["authenticated"], "The user should be able to access this endpoint.")


class UsersTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):
        user = User.objects.create_user(username="Heffalumps", email="heffalumps@woozles.com", password="Woozles")
        UserRole.objects.create(name=ADMIN, user=user)

    # Tests if we can get all staff members from our database
    def test_get_staff_members(self):
        # Register supervisors
        create_new_user("Yeesha", "Woozles", user_type=SUPERVISOR)
        create_new_user("Yeesah2", "Woozles", user_type=SUPERVISOR)

        # Login as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        staff_response = self.client.get(path="/api/auth/all_staff/",
                                         HTTP_AUTHORIZATION='JWT {}'.format(token))
        staff_response_content = json.loads(staff_response.content.decode('utf-8'))

        self.assertEqual(len(staff_response_content), 3, "There should be 2 supervisors and 1 admin in the system.")

    # Tests if we can get all supervisor staff members from our database
    def test_get_supervisor_staff_members(self):
        # Register supervisors
        create_new_user("Yeesha", "Woozles", user_type=SUPERVISOR)
        create_new_user("Yeesah2", "Woozles", user_type=SUPERVISOR)

        # Login as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        staff_response = self.client.get(path="/api/auth/supervisor_staff/",
                                         HTTP_AUTHORIZATION='JWT {}'.format(token))
        staff_response_content = json.loads(staff_response.content.decode('utf-8'))

        self.assertEqual(len(staff_response_content), 2, "There should be 2 supervisors in the system.")

    # Tests if we can change the role of specific staff members in our database
    def test_change_staff_roles(self):
        # Register a supervisor
        create_new_user("Yeesha", "Woozles", user_type=SUPERVISOR)

        # Login as the supervisor
        token = log_in(self.client, "Yeesha", "Woozles")

        staff_response = self.client.post("/api/auth/staff_roles/",
                                          json.dumps({'new_user_roles': {'Heffalumps': SUPERVISOR}}),
                                          HTTP_AUTHORIZATION='JWT {}'.format(token),
                                          content_type="application/json")

        self.assertEquals(staff_response.status_code, 400)

        # Login as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        staff_response = self.client.post("/api/auth/staff_roles/",
                                          json.dumps({'new_user_roles': {'Yeesha': ADMIN}}),
                                          HTTP_AUTHORIZATION='JWT {}'.format(token),
                                          content_type="application/json")

        self.assertEquals(staff_response.status_code, 200)

    # Tests if we can get the list of all supervisors' usernames
    def test_get_supervisor_usernames(self):
        # Register supervisor
        create_new_user("Yeesha", "Woozles", user_type=SUPERVISOR)

        # Login as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        supervisor_response = self.client.get(path="/api/auth/supervisor_usernames/", data={},
                                              HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(supervisor_response.status_code, 200)

        statistics_response_content = json.loads(supervisor_response.content.decode('utf-8'))
        self.assertEqual(len(statistics_response_content["usernames"]), 1)
        self.assertEqual(statistics_response_content["usernames"][0], "Yeesha")

