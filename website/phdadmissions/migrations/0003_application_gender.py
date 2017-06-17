# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0002_auto_20170616_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='gender',
            field=models.CharField(choices=[('FEMALE', 'Female'), ('MALE', 'Male')], default='FEMALE', max_length=100),
            preserve_default=False,
        ),
    ]
