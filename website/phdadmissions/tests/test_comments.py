import json
from assets.constants import *

from phdadmissions.models.application import Application
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import create_new_application, create_application_details, create_new_user, \
    log_in


class CommentsTestCase(BaseTestCase):

    # Tests if a supervisor can add a new comment
    def test_add_new_comment(self):

        # Register a supervisor
        create_new_user("Atrus1", "Woozles", user_type=SUPERVISOR)

        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

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
        token = log_in(self.client, "Atrus1", "Woozles")

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

    # Tests if an admin can comment under an application without a supervision initially
    def test_add_new_comment_as_admin(self):

        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # New application
        create_new_application(token, create_application_details(self.academic_year.id), self.client)
        latest_application = Application.objects.latest(field_name="created_at")

        # Register a new admin
        create_new_user("Atrus", "Atruuus", user_type=ADMIN)

        # Log in as the new admin
        token = log_in(self.client, "Atrus", "Atruuus")

        # Add comment
        new_comment_response = self.client.post("/api/applications/comment/", {
            "application_id": latest_application.id,
            "content": "This application is awesome!",
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_comment_response.status_code, 200)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(len(latest_application.supervisions.all()), 2)
