# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0009_auto_20170613_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='academicyear',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
