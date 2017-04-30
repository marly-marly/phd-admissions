# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0006_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(default='PENDING', blank=True, choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('REJECT_TO_MSC', 'Rejected to MSc'), ('WITHDRAWN', 'Withdrawn')], max_length=100),
        ),
        migrations.AlterField(
            model_name='supervision',
            name='recommendation',
            field=models.CharField(default='NOT_VIEWED', blank=True, choices=[('NOT_VIEWED', 'Not viewed'), ('WAIT_TO_INTERVIEW', 'Wait to interview'), ('REJECT_TO_MSC', 'Reject to MSc'), ('REJECT_TO_MAC', 'Reject to MAC'), ('STRAIGHT_REJECT', 'Straight reject'), ('ACCEPT_BUT_NOT_SUPERVISED', 'Accept but not supervised'), ('ACCEPT_AND_SUPERVISED', 'Accept and supervised'), ('OTHER', 'Other')], max_length=100),
        ),
    ]
