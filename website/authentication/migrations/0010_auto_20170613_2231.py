# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_auto_20170612_0022'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(max_length=100, choices=[('SUPER_ADMIN', 'SUPER_ADMIN'), ('ADMIN', 'ADMIN'), ('SUPERVISOR', 'SUPERVISOR')]),
        ),
    ]