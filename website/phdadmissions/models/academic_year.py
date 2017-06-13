from django.db import models


# Specifies an academic year
class AcademicYear(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)

    default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Maintain only 1 default = true among all entities.
    def save(self, *args, **kwargs):
        if self.default:
            try:
                temp = AcademicYear.objects.get(default=True)
                if self != temp:
                    temp.default = False
                    temp.save()
            except AcademicYear.DoesNotExist:
                pass
        super(AcademicYear, self).save(*args, **kwargs)


