# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0008_auto_20170611_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicyear',
            name='default',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(max_length=100, choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('REJECT_TO_MSC', 'Rejected to MSc'), ('WITHDRAWN', 'Withdrawn'), ('DEFERRED', 'Deferred')], default='PENDING', blank=True),
        ),
    ]
