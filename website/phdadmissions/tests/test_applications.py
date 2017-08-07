import json
from assets.constants import *

from phdadmissions.models.application import Application
from phdadmissions.models.supervision import Supervision
from phdadmissions.tests.base_test_case import BaseTestCase
from phdadmissions.tests.helper_functions import create_new_application, create_application_details, create_new_user, \
    log_in


class ApplicationsTestCase(BaseTestCase):

    # Tests if the administrator can add a new application, and if we can get the data as well
    def test_new_phd_application(self):

        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # Register two supervisors
        create_new_user("Atrus1", "Woozles", user_type=SUPERVISOR)
        create_new_user("Atrus2", "Woozles", user_type=SUPERVISOR)

        # New application
        new_application_response = create_new_application(token, create_application_details(self.academic_year.id),
                                                          self.client)
        self.assertEqual(new_application_response.status_code, 201)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(latest_application.forename, "Marton")
        self.assertEqual(latest_application.status, PENDING_STATUS)
        self.assertEqual(latest_application.administrator_comment, None)
        self.assertEqual(len(latest_application.supervisions.filter(type=SUPERVISOR)), 2)
        self.assertEqual(len(latest_application.tags.all()), 2)

        # Update application
        put_data = json.loads(
            create_application_details(self.academic_year.id, registry_ref="9874334", surname="Szeles",
                                       forename="Martin",
                                       possible_funding=["SELF"], funding_status="PENDING", origin="EU",
                                       student_type="COMPUTING", status="PENDING",
                                       supervisors=[],
                                       research_subject="Investigating travelling at the speed of light.",
                                       administrator_comment="Awesome", file_descriptions=[]))

        update_json = json.dumps({"id": latest_application.id, "application": put_data})
        update_application_response = self.client.put(path="/api/applications/application/",
                                                      data=update_json,
                                                      HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                      content_type='application/json')

        self.assertEqual(update_application_response.status_code, 200)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(latest_application.forename, "Martin")
        self.assertEqual(latest_application.administrator_comment, "Awesome")

        # Check if we can read the data through the endpoint
        search_result_response = self.client.get("/api/applications/application/", {"id": latest_application.id},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))
        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        application = search_result_response_content["application"]
        self.assertEqual(application["forename"], "Martin")
        self.assertEqual(len(application["supervisions"]), 3)

        # Delete
        delete_application_response = self.client.delete(path="/api/applications/application/",
                                                         data=json.dumps({"id": application["id"]}),
                                                         HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                         content_type='application/json')

        self.assertEqual(delete_application_response.status_code, 204)

    # Tests if the administrator can add or delete a supervision corresponding to an application
    def test_add_and_delete_supervision(self):

        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # Register a supervisor
        create_new_user("Atrus1", "Woozles", user_type=SUPERVISOR)

        # New application
        create_new_application(token, create_application_details(self.academic_year.id, supervisors=[]), self.client)
        latest_application = Application.objects.latest(field_name="created_at")

        # Add supervision
        new_supervision_response = self.client.post("/api/applications/supervision/", {
            "id": latest_application.id,
            "supervisor": "Atrus1"
        }, HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(new_supervision_response.status_code, 200)

        response_content = json.loads(new_supervision_response.content.decode('utf-8'))
        self.assertEqual(response_content["supervisor"]["username"], "Atrus1")

        latest_application = Application.objects.latest(field_name="created_at")
        supervisions = latest_application.supervisions.all()
        self.assertEqual(len(supervisions), 2, "We expect 2 supervisions, because one belongs to the admins.")

        # Allocate supervision
        self.assertEqual(response_content["allocated"], False)
        supervision_id = response_content["id"]
        self.client.post("/api/applications/supervision_allocation/",
                         {"supervision_id": supervision_id},
                         HTTP_AUTHORIZATION='JWT {}'.format(token))

        supervision = Supervision.objects.filter(id=supervision_id).first()
        self.assertEqual(supervision.allocated, True)

        post_data = json.dumps({"supervision_id": supervision_id})
        self.client.delete("/api/applications/supervision_allocation/", data=post_data,
                           HTTP_AUTHORIZATION='JWT {}'.format(token))

        supervision = Supervision.objects.filter(id=supervision_id).first()
        self.assertEqual(supervision.allocated, False)

        # Delete supervision
        post_data = json.dumps({"id": latest_application.id, "supervisor": "Atrus1",
                                "supervision_id": supervisions.filter(type=SUPERVISOR).first().id})
        self.client.delete("/api/applications/supervision/", data=post_data, HTTP_AUTHORIZATION='JWT {}'.format(token))

        latest_application = Application.objects.latest(field_name="created_at")
        supervisions = latest_application.supervisions.all()
        self.assertEqual(len(supervisions), 1)

    # Tests if we can search for applications
    def test_application_search(self):

        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        # New applications
        post_data = create_application_details(self.academic_year.id, registry_ref="012983234", surname="Szeles",
                                               forename="Marton",
                                               possible_funding=["SELF"], funding_status="PENDING", origin="EU",
                                               student_type="COMPUTING",
                                               supervisors=[],
                                               research_subject="Investigating travelling at the speed of light.",
                                               administrator_comment=None, file_descriptions=[], tags=["Ferrari"])
        create_new_application(token, post_data, self.client)

        post_data = create_application_details(self.academic_year.id, registry_ref="7374636", surname="Atrus",
                                               forename="Yeesha",
                                               possible_funding=["SELF"], funding_status="PENDING",
                                               origin="OVERSEAS",
                                               student_type="COMPUTING_AND_CDT",
                                               supervisors=[],
                                               research_subject="Investigating writing linking books.",
                                               administrator_comment=None, file_descriptions=[],
                                               tags=["Porsche", "Mercedes", "Ferrari"])
        create_new_application(token, post_data, self.client)

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"surname": "Szeles"},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 1)

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"forename": "a"},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 2)

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"forename": "a", "origin": "EU"},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 1)

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"origin": ["EU", "OVERSEAS"]},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 2)

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"tags": ["Porsche", "Mercedes"]},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 1)

        # Search
        search_result_response = self.client.get("/api/applications/search/", {"tags": ["Ferrari"]},
                                                 HTTP_AUTHORIZATION='JWT {}'.format(token))

        search_result_response_content = json.loads(search_result_response.content.decode('utf-8'))
        applications = search_result_response_content["applications"]
        self.assertEqual(len(applications), 2)

    # Tests if we can get the list of newFilesIndex for the application form
    def test_get_application_choices(self):

        # Log in as the admin
        token = log_in(self.client, "Heffalumps", "Woozles")

        choices_response = self.client.get(path="/api/applications/newFilesIndex/application/", data={},
                                           HTTP_AUTHORIZATION='JWT {}'.format(token))

        choices_response_content = json.loads(choices_response.content.decode('utf-8'))
        self.assertEqual(len(choices_response_content["possible_funding"]), 7)
