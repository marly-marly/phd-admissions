from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.test import Client
import json
from assets.constants import *
from datetime import datetime
from django.utils import timezone

from phdadmissions.models.academic_year import AcademicYear
from phdadmissions.models.application import Application
from phdadmissions.tests.helper_functions import create_new_application, create_application_details


class ApplicationsTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):
        self.response = self.client.post("/api/auth/register/", {"username": "Heffalumps",
                                                                 "email": "heffalumps@woozles.com",
                                                                 "password": "Woozles"})

        # New academic year
        self.academic_year = AcademicYear.objects.create(name="17/18", start_date=timezone.now(),
                                                         end_date=timezone.now(), default=True)

    # Tests if the administrator can add a new application, and if we can get the data as well
    def test_new_phd_application(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # Register two supervisors
        self.client.post("/api/auth/register/", {"username": "Atrus1",
                                                 "email": "atrus1@woozles.com",
                                                 "password": "Woozles",
                                                 "user_type": "SUPERVISOR"})

        self.client.post("/api/auth/register/", {"username": "Atrus2",
                                                 "email": "atrus2@woozles.com",
                                                 "password": "Woozles",
                                                 "user_type": "SUPERVISOR"})

        # New application
        new_application_response = create_new_application(token, create_application_details(self.academic_year.id),
                                                          self.client)
        self.assertEqual(new_application_response.status_code, 201)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(latest_application.forename, "Marton")
        self.assertEqual(latest_application.status, PENDING_STATUS)
        self.assertEqual(latest_application.registry_comment, None)
        self.assertEqual(len(latest_application.supervisions.filter(type=SUPERVISOR)), 2)

        # Update application
        put_data = json.loads(
            create_application_details(self.academic_year.id, registry_ref="9874334", surname="Szeles",
                                       forename="Martin",
                                       possible_funding=["SELF"], funding_status="PENDING", origin="EU",
                                       student_type="COMPUTING", status="PENDING",
                                       supervisors=[],
                                       research_subject="Investigating travelling at the speed of light.",
                                       registry_comment="Awesome", file_descriptions=[]))

        update_application_response = self.client.put(path="/api/applications/application/",
                                                      data=json.dumps(
                                                          {"id": latest_application.id, "application": put_data}),
                                                      HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                      content_type='application/json')

        self.assertEqual(update_application_response.status_code, 200)

        latest_application = Application.objects.latest(field_name="created_at")
        self.assertEqual(latest_application.forename, "Martin")
        self.assertEqual(latest_application.registry_comment, "Awesome")

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
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # Register a supervisor
        self.client.post("/api/auth/register/", {"username": "Atrus1",
                                                 "email": "atrus1@woozles.com",
                                                 "password": "Woozles",
                                                 "user_type": "SUPERVISOR"})

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

        # Delete supervision
        post_data = json.dumps({"id": latest_application.id, "supervisor": "Atrus1",
                                "supervision_id": supervisions.filter(type=SUPERVISOR).first().id})
        self.client.delete("/api/applications/supervision/", data=post_data, HTTP_AUTHORIZATION='JWT {}'.format(token))

        latest_application = Application.objects.latest(field_name="created_at")
        supervisions = latest_application.supervisions.all()
        self.assertEqual(len(supervisions), 1)

    # Tests if we can search for applications
    def test_application_search(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        # New applications
        post_data = create_application_details(self.academic_year.id, registry_ref="012983234", surname="Szeles",
                                               forename="Marton",
                                               possible_funding=["SELF"], funding_status="PENDING", origin="EU",
                                               student_type="COMPUTING",
                                               supervisors=[],
                                               research_subject="Investigating travelling at the speed of light.",
                                               registry_comment=None, file_descriptions=[])
        create_new_application(token, post_data, self.client)

        post_data = create_application_details(self.academic_year.id, registry_ref="7374636", surname="Atrus",
                                               forename="Yeesha",
                                               possible_funding=["SELF"], funding_status="PENDING",
                                               origin="OVERSEAS",
                                               student_type="COMPUTING_AND_CDT",
                                               supervisors=[],
                                               research_subject="Investigating writing linking books.",
                                               registry_comment=None, file_descriptions=[])
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

    # Tests if we can get the list of newFilesIndex for the application form
    def test_get_application_choices(self):
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})

        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        choices_response = self.client.get(path="/api/applications/newFilesIndex/application/", data={},
                                           HTTP_AUTHORIZATION='JWT {}'.format(token))

        choices_response_content = json.loads(choices_response.content.decode('utf-8'))
        self.assertEqual(len(choices_response_content["possible_funding"]), 7)

    # Tests if we can get the staistics of all applications
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

    # Tests if we can get the list of all supervisors' usernames
    def test_get_supervisor_usernames(self):
        # Register supervisor
        self.client.post("/api/auth/register/", {"username": "Yeesha",
                                                 "email": "yeesha@woozles.com",
                                                 "password": "Woozles",
                                                 "user_type": "SUPERVISOR"})

        # Login
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})
        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        supervisor_response = self.client.get(path="/api/applications/supervisor/", data={},
                                              HTTP_AUTHORIZATION='JWT {}'.format(token))

        self.assertEqual(supervisor_response.status_code, 200)

        statistics_response_content = json.loads(supervisor_response.content.decode('utf-8'))
        self.assertEqual(len(statistics_response_content["usernames"]), 1)
        self.assertEqual(statistics_response_content["usernames"][0], "Yeesha")

    # Tests if we can successfully retrieve, upload, update, and delete an academic year from the database
    def test_manage_academic_years(self):
        # Login
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})
        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        latest_academic_year = AcademicYear.objects.latest(field_name="created_at")

        # Get
        get_academic_year_response = self.client.get(path="/api/applications/admin/academic_year",
                                                     HTTP_AUTHORIZATION='JWT {}'.format(token))
        response_content = json.loads(get_academic_year_response.content.decode('utf-8'))
        self.assertEqual(len(response_content["academic_years"]), 1)
        self.assertEqual(response_content["academic_years"][0]["name"], "17/18")

        # Update
        post_data = json.dumps({"id": latest_academic_year.id,
                                "academic_year": {"name": "16/17"}})

        update_academic_year_response = self.client.put(path="/api/applications/admin/academic_year",
                                                        data=post_data,
                                                        HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                        content_type='application/json')

        self.assertEqual(update_academic_year_response.status_code, 200)
        latest_academic_year = AcademicYear.objects.latest(field_name="created_at")
        self.assertEqual(latest_academic_year.name, "16/17")

        # Delete
        post_data = json.dumps({"id": latest_academic_year.id})
        delete_academic_year_response = self.client.delete(path="/api/applications/admin/academic_year",
                                                           data=post_data,
                                                           HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                           content_type='application/json')

        self.assertEqual(delete_academic_year_response.status_code, 204)
        all_academic_years = AcademicYear.objects.all()
        self.assertEqual(len(all_academic_years), 0)

    # Tests if we can successfully update the default field of an academic year
    def test_update_default_academic_year(self):
        # Login
        response = self.client.post("/api/auth/login/", {"username": "Heffalumps", "password": "Woozles"})
        response_content = json.loads(response.content.decode('utf-8'))
        token = response_content["token"]

        latest_academic_year = AcademicYear.objects.latest(field_name="created_at")

        # Update default
        post_data = json.dumps({"id": latest_academic_year.id,
                                "academic_year": {"default": True}})

        self.client.put(path="/api/applications/admin/academic_year",
                        data=post_data,
                        HTTP_AUTHORIZATION='JWT {}'.format(token),
                        content_type='application/json')

        latest_academic_year = AcademicYear.objects.latest(field_name="created_at")
        self.assertEqual(latest_academic_year.default, True)

        # Upload new application
        start_time = datetime.now()
        end_time = datetime.now()

        post_data = json.dumps({"name": "16/17",
                                "start_date": start_time,
                                "end_date": end_time,
                                "default": True}, cls=DjangoJSONEncoder)

        new_academic_year_response = self.client.post(path="/api/applications/admin/academic_year",
                                                      data=post_data,
                                                      HTTP_AUTHORIZATION='JWT {}'.format(token),
                                                      content_type='application/json')

        self.assertEqual(new_academic_year_response.status_code, 201)

        true_academic_years = AcademicYear.objects.filter(default=True)
        self.assertEqual(len(true_academic_years), 1)
        self.assertEqual(true_academic_years[0].name, "16/17")

        # Update default
        post_data = json.dumps({"id": latest_academic_year.id,
                                "academic_year": {"default": True}})

        self.client.put(path="/api/applications/admin/academic_year",
                        data=post_data,
                        HTTP_AUTHORIZATION='JWT {}'.format(token),
                        content_type='application/json')

        true_academic_years = AcademicYear.objects.filter(default=True)
        self.assertEqual(len(true_academic_years), 1)
        self.assertEqual(true_academic_years[0].name, "17/18")
