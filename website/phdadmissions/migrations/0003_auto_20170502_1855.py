# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0002_documentation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supervision',
            name='supervisor',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='supervisions'),
        ),
    ]
