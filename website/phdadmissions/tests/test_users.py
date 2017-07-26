import json

from assets.constants import SUPERVISOR, ADMIN
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import create_new_user, log_in, create_new_application, \
    create_application_details


class UsersTestCase(BaseTestCase):
    # Tests if we can get all staff members from our database
    def test_get_staff_members(self):
        # Register supervisors
        create_new_user("Yeesha", "Woozles", user_type=SUPERVISOR)
        create_new_user("Yeesah2", "Woozles", user_type=SUPERVISOR)

        # Login as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        staff_response = self.client.get(path="/api/auth/staff/",
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

        supervisor_response = self.client.get(path="/api/auth/supervisor/", data={},
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
