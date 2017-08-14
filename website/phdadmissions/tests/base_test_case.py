from django.test import Client
from django.test import TestCase
from django.utils import timezone

from phdadmissions.models.academic_year import AcademicYear
from authentication.tests.helper_functions import create_new_user


class BaseTestCase(TestCase):
    client = Client()
    response = None

    def setUp(self):

        # New admin user
        create_new_user("Heffalumps", "Woozles")

        # New academic year
        self.academic_year = AcademicYear.objects.create(name="17/18", start_date=timezone.now(),
                                                         end_date=timezone.now(), default=True)
