import json

from assets.constants import EMAIL
from phdadmissions.models.configuration import Configuration
from phdadmissions.tests.base_test_case import BaseTestCase
from authentication.tests.helper_functions import log_in


class ConfigurationsTestCase(BaseTestCase):
    # Tests if the email configuration can be successfully edited
    def test_update_and_get_email_config(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # GET
        email_configuration_response = self.client.get("/api/phd/admin/email/",
                                                       HTTP_AUTHORIZATION='JWT {}'.format(token))
        response_content = json.loads(email_configuration_response.content.decode('utf-8'))
        self.assertEqual(email_configuration_response.status_code, 200)
        self.assertEqual(response_content['value'], "")

        # UPDATE
        post_data = json.dumps({"value": "<b>Hello</b>"})

        update_email_configuration_response = self.client.put(path="/api/phd/admin/email/",
                                                              data=post_data,
                                                              HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                              content_type='application/json')

        self.assertEqual(update_email_configuration_response.status_code, 200)
        self.assertEqual(Configuration.objects.filter(name=EMAIL).first().value, "<b>Hello</b>")
