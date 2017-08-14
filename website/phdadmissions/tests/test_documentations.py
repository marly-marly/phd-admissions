import json

from assets.constants import SUPERVISOR, APPLICATION_FORM
from phdadmissions.models.application import Application
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import create_new_application, create_application_details
from authentication.tests.helper_functions import create_new_user, log_in


class DocumentationsTestCase(BaseTestCase):
    # Tests if the appropriate supervisor can upload a documentation to their supervision
    def test_new_phd_application(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # Register two supervisors
        create_new_user("Atrus1", "Woozles", user_type=SUPERVISOR)
        create_new_user("Atrus2", "Woozles", user_type=SUPERVISOR)

        # New application
        create_new_application(token, create_application_details(self.academic_year.id, registry_ref="01",
                                                                 supervisors=['Atrus1', 'Atrus2']), self.client)

        # Log in as Atrus1
        token = log_in(self.client, "Atrus1", "Woozles")

        # POST new file
        application = Application.objects.filter(registry_ref="01").first()
        supervision = application.supervisions.filter(supervisor__username="Atrus1").first()
        request_details = json.dumps({"supervision_id": supervision.id,
                                      "file_descriptions": {'APPLICATION_FORM_1': 'This is my description.'}})

        with open('phdadmissions/tests/test_file.pdf') as fp:
            file_response = self.client.post('/api/phd/file/',
                                             {'details': request_details, 'APPLICATION_FORM_1': fp},
                                             HTTP_AUTHORIZATION='JWT {}'.format(token), )
            self.assertEqual(file_response.status_code, 201)
            fp.close()

        supervision = application.supervisions.filter(supervisor__username="Atrus1").first()
        self.assertEqual(supervision.documentations.count(), 1)
        documentation = supervision.documentations.first()
        self.assertEqual(documentation.file_type, APPLICATION_FORM)
        self.assertEqual(documentation.description, 'This is my description.')

        # Download the file
        download_response = self.client.get("/api/phd/download/", {"id": documentation.id, "token": token})
        self.assertEquals(
            download_response.get('Content-Disposition'),
            'attachment; filename=' + documentation.file_name
        )

        # DELETE file
        delete_file_response = self.client.delete(path="/api/phd/file/",
                                                  data=json.dumps({"file_id": documentation.id}),
                                                  HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                  content_type='application/json')

        self.assertEqual(delete_file_response.status_code, 204)
        supervision = application.supervisions.filter(supervisor__username="Atrus1").first()
        self.assertEqual(supervision.documentations.count(), 0)

    # Tests if we can successfully download a ZIP file
    def test_download_zip(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # Register two supervisors
        create_new_user("Atrus1", "Woozles", user_type=SUPERVISOR)
        create_new_user("Atrus2", "Woozles", user_type=SUPERVISOR)

        # New application
        create_new_application(token, create_application_details(self.academic_year.id, registry_ref="01",
                                                                 supervisors=['Atrus1', 'Atrus2']), self.client)

        # Log in as Atrus1
        token = log_in(self.client, "Atrus1", "Woozles")

        # POST new file
        application = Application.objects.filter(registry_ref="01").first()
        supervision = application.supervisions.filter(supervisor__username="Atrus1").first()
        request_details = json.dumps({"supervision_id": supervision.id,
                                      "file_descriptions": {'APPLICATION_FORM_1': 'This is my description.'}})

        with open('phdadmissions/tests/test_file.pdf') as fp:
            self.client.post('/api/phd/file/',
                             {'details': request_details, 'APPLICATION_FORM_1': fp},
                             HTTP_AUTHORIZATION='JWT {}'.format(token), )

        download_response = self.client.get("/api/phd/zip_download/", {"token": token,
                                                                       "application_ids": [application.id],
                                                                       "sort_field": "registry_ref",
                                                                       "sort_by": "DESC",
                                                                       "selected_fields": ["registry_ref",
                                                                                           "forename"]})
        self.assertEquals(download_response.get('Content-Type'), 'application/x-zip-compressed')

    # Tests if we can successfully download a CSV file
    def test_download_csv(self):
        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # Register two supervisors
        create_new_user("Atrus1", "Woozles", user_type=SUPERVISOR)
        create_new_user("Atrus2", "Woozles", user_type=SUPERVISOR)

        # New application
        create_new_application(token, create_application_details(self.academic_year.id, registry_ref="01",
                                                                 supervisors=['Atrus1', 'Atrus2']), self.client)

        application = Application.objects.filter(registry_ref="01").first()
        download_response = self.client.get("/api/phd/csv_download/", {"token": token,
                                                                       "application_ids": [application.id],
                                                                       "sort_field": "registry_ref",
                                                                       "sort_by": "DESC",
                                                                       "selected_fields": ["registry_ref",
                                                                                           "forename"]})
        self.assertEquals(download_response.get('Content-Type'), 'text/csv')
