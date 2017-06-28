import json

from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import create_new_application, create_application_details, log_in


class StatisticsTestCase(BaseTestCase):

    # Tests if we can get the statistics of all applications
    def test_get_application_statistics(self):

        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # New application
        create_new_application(token, create_application_details(self.academic_year.id), self.client)

        statistics_response = self.client.get(path="/api/applications/statistics/", data={},
                                              HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(statistics_response.status_code, 200)

        statistics_response_content = json.loads(statistics_response.content.decode('utf-8'))
        self.assertEqual(statistics_response_content["number_of_applications"], 1)