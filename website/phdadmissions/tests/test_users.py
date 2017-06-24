import json

from django.test import TestCase
from django.test import Client
from django.utils import timezone

from phdadmissions.models.academic_year import AcademicYear


class UsersTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):
        self.response = self.client.post("/api/auth/register/", {"username": "Heffalumps",
                                                                 "email": "heffalumps@woozles.com",
                                                                 "password": "Woozles"})

        # New academic year
        self.academic_year = AcademicYear.objects.create(name="17/18", start_date=timezone.now(),
                                                         end_date=timezone.now(), default=True)

    # Tests if we can get the list of all supervisors' usernames
    def test_get_supervisor_usernames(self):
        # Register supervisor
        self.client.post("/api/auth/register/", {"username": "Yeesha",
                                                 "email": "yeesha@woozles.com",
                                                 "password": "Woozles",
                                                 "user_type": "SUPERVISOR"})

        # Login
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})
        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        supervisor_response = self.client.get(path="/api/applications/supervisor/", data={},
                                              HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(supervisor_response.status_code, 200)

        statistics_response_content = json.loads(supervisor_response.content.decode('utf-8'))
        self.assertEqual(len(statistics_response_content["usernames"]), 1)
        self.assertEqual(statistics_response_content["usernames"][0], "Yeesha")