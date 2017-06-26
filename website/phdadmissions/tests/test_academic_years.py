from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from django.test import Client
import json
from datetime import datetime
from django.utils import timezone

from phdadmissions.models.academic_year import AcademicYear


class AcademicYearsTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):
        self.response = self.client.post("/api/auth/register/", {"username": "Heffalumps",
                                                                 "email": "heffalumps@woozles.com",
                                                                 "password": "Woozles"})

        # New academic year
        self.academic_year = AcademicYear.objects.create(name="17/18", start_date=timezone.now(),
                                                         end_date=timezone.now(), default=True)

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