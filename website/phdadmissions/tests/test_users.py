import json

from assets.constants import SUPERVISOR
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import create_new_user, log_in, create_new_application, \
    create_application_details


class UsersTestCase(BaseTestCase):
    # Tests if we can get the list of all supervisors' usernames
    def test_get_supervisor_usernames(self):
        # Register supervisor
        create_new_user("Yeesha", "Woozles", user_type=SUPERVISOR)

        # Login as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        supervisor_response = self.client.get(path="/api/applications/supervisor/", data={},
                                              HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(supervisor_response.status_code, 200)

        statistics_response_content = json.loads(supervisor_response.content.decode('utf-8'))
        self.assertEqual(len(statistics_response_content["usernames"]), 1)
        self.assertEqual(statistics_response_content["usernames"][0], "Yeesha")

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

        recommended_supervisors_response = self.client.get(path="/api/applications/recommended_supervisors/",
                                                           data={'tags': ['Porsche', 'Ferrari']},
                                                           HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(recommended_supervisors_response.status_code, 200)
        response_content = json.loads(recommended_supervisors_response.content.decode('utf-8'))
        self.assertEqual(len(response_content), 2)
        self.assertEqual(response_content[0]['total'], 2)
        self.assertEqual(response_content[0]['username'], 'Yeesha')
