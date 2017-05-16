# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_auto_20170515_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(choices=[('SUPER_ADMIN', 'SUPER_ADMIN'), ('ADMIN', 'ADMIN'), ('SUPERVISOR', 'SUPERVISOR')], max_length=100),
        ),
    ]
