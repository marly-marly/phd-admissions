# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0005_auto_20170515_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='supervision',
            name='creator',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='supervision',
            name='type',
            field=models.CharField(default='SUPERVISOR', choices=[('ADMIN', 'Administrator'), ('SUPERVISOR', 'Supervisor')], max_length=100),
        ),
    ]
