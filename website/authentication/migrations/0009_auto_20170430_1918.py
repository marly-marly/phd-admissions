# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_auto_20170429_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(choices=[('ADMIN', 'ADMIN'), ('SUPER_ADMIN', 'SUPER_ADMIN'), ('SUPERVISOR', 'SUPERVISOR')], max_length=100),
        ),
    ]