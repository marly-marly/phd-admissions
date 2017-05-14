# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0003_auto_20170502_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentation',
            name='file_name',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
