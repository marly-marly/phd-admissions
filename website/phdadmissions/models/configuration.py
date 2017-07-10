from django.db import models


# Specifies the details of name-value configurations
class Configuration(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)
    value = models.TextField(null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
