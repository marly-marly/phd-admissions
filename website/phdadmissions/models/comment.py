from django.db import models
from django.db.models import TextField

from phdadmissions.models.supervision import Supervision


# Specifies the comments made by users
class Comment(models.Model):
    supervision = models.ForeignKey(Supervision, related_name='comments', null=False)
    content = TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


