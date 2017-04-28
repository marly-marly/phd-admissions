# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='registry_comment',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='research_subject',
            field=models.CharField(null=True, max_length=255),
        ),
    ]
