# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_auto_20170611_2221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(max_length=100, choices=[('ADMIN', 'ADMIN'), ('SUPER_ADMIN', 'SUPER_ADMIN'), ('SUPERVISOR', 'SUPERVISOR')]),
        ),
    ]