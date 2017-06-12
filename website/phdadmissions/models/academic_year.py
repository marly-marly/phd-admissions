from django.db import models


# Specifies an academic year
class AcademicYear(models.Model):
    name = models.CharField(max_length=255, null=False)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


