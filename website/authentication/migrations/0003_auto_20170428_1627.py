# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20170428_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrole',
            name='name',
            field=models.CharField(choices=[('supervisor', 'supervisor'), ('admin', 'admin'), ('super_admin', 'super_admin')], max_length=100),
        ),
    ]
