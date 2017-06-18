# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_auto_20170616_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(max_length=100, choices=[('ADMIN', 'ADMIN'), ('SUPERVISOR', 'SUPERVISOR'), ('SUPER_ADMIN', 'SUPER_ADMIN')]),
        ),
    ]