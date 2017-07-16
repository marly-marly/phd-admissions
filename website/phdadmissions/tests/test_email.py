import json

from django.contrib.auth.models import User

from assets.constants import SUPERVISOR
from phdadmissions.models.application import Application
from phdadmissions.models.supervision import Supervision
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import log_in, create_new_user, create_new_application, \
    create_application_details


class EmailTestCase(BaseTestCase):
    # Tests if we get successfully get a preview for the supervisor email
    def test_get_email_preview(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # New application
        create_new_application(token,
                               create_application_details(self.academic_year.id, supervisors=[], registry_ref="012345"),
                               self.client)
        latest_application = Application.objects.latest(field_name="created_at")

        # Register a supervisor
        create_new_user("Atrus1", "Woozles", user_type=SUPERVISOR)
        supervisor = User.objects.get(username="Atrus1")
        supervisor.first_name = "Atrus"
        supervisor.last_name = "Venus"
        supervisor.save()

        # Add supervision
        new_supervision = Supervision.objects.create(application=latest_application, supervisor=supervisor)

        # Get the email preview
        email_preview_response = self.client.post("/api/applications/admin/email_preview/", {
            "email_template": "<b>Dear Chanapata</b><hr><p>{{supervisor_first_name}} {{supervisor_last_name}} {{registry_ref}}",
            "supervision_id": new_supervision.id
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        response_content = email_preview_response
        self.assertContains(response_content, latest_application.registry_ref)
        self.assertContains(response_content, supervisor.first_name)
        self.assertContains(response_content, supervisor.last_name)

        # Get the email preview without a template
        email_preview_response = self.client.post("/api/applications/admin/email_preview/", {
            "email_template": ""
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        response_content = email_preview_response
        self.assertEquals(response_content.status_code, 200)

    # Tests if we get successfully send an email
    def test_send_email(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # New application
        create_new_application(token,
                               create_application_details(self.academic_year.id, supervisors=[], registry_ref="012345"),
                               self.client)
        latest_application = Application.objects.latest(field_name="created_at")

        # Register a supervisor
        create_new_user("Atrus1", "Woozles", user_type=SUPERVISOR, email="atrus@mail.com")
        supervisor = User.objects.get(username="Atrus1")

        # Add supervision
        new_supervision = Supervision.objects.create(application=latest_application, supervisor=supervisor)

        # Attempt to send the email with missing arguments
        email_send_response = self.client.post("/api/applications/admin/email_send/", {
            "supervision_id": new_supervision.id
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEquals(email_send_response.status_code, 400)

        # Attempt to send the email with missing arguments
        email_send_response = self.client.post("/api/applications/admin/email_send/", {
            "email_template": ""
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEquals(email_send_response.status_code, 400)
