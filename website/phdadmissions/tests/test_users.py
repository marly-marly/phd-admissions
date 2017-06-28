import json

from assets.constants import SUPERVISOR
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import create_new_user, log_in


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