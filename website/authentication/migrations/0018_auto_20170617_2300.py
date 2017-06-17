# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0017_auto_20170616_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(choices=[('ADMIN', 'ADMIN'), ('SUPERVISOR', 'SUPERVISOR'), ('SUPER_ADMIN', 'SUPER_ADMIN')], max_length=100),
        ),
    ]
