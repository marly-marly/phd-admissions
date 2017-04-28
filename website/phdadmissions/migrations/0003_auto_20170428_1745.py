# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0002_auto_20170428_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.CharField(max_length=100, default='PENDING', choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('REJECT_TO_MSC', 'Rejected to MSc'), ('WITHDRAWN', 'Withdrawn')]),
        ),
        migrations.AlterField(
            model_name='application',
            name='funding_status',
            field=models.CharField(max_length=100, default='PENDING', choices=[('PENDING', 'Pending'), ('AWARDED', 'Awarded')]),
        ),
    ]
