# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0018_auto_20170617_2300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(max_length=100, choices=[('SUPERVISOR', 'SUPERVISOR'), ('ADMIN', 'ADMIN'), ('SUPER_ADMIN', 'SUPER_ADMIN')]),
        ),
    ]
