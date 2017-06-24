import json

from django.test import TestCase
from django.test import Client
from django.utils import timezone

from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.tests.helper_functions import create_new_application, create_application_details


class StatisticsTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):
        self.response = self.client.post("/api/auth/register/", {"username": "Heffalumps",
                                                                 "email": "heffalumps@woozles.com",
                                                                 "password": "Woozles"})

        # New academic year
        self.academic_year = AcademicYear.objects.create(name="17/18", start_date=timezone.now(),
                                                         end_date=timezone.now(), default=True)

    # Tests if we can get the statistics of all applications
    def test_get_application_statistics(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # New application
        create_new_application(token, create_application_details(self.academic_year.id), self.client)

        statistics_response = self.client.get(path="/api/applications/statistics/", data={},
                                              HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(statistics_response.status_code, 200)

        statistics_response_content = json.loads(statistics_response.content.decode('utf-8'))
        self.assertEqual(statistics_response_content["number_of_applications"], 1)