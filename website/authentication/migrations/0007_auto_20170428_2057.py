# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_auto_20170428_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(choices=[('SUPERVISOR', 'SUPERVISOR'), ('ADMIN', 'ADMIN'), ('SUPER_ADMIN', 'SUPER_ADMIN')], max_length=100),
        ),
    ]
