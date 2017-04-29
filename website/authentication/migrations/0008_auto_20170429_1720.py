# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_auto_20170428_2057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(choices=[('SUPER_ADMIN', 'SUPER_ADMIN'), ('SUPERVISOR', 'SUPERVISOR'), ('ADMIN', 'ADMIN')], max_length=100),
        ),
    ]
