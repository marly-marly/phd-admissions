# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0004_documentation_file_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='registry_ref',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only digits are allowed.')], unique=True),
        ),
    ]
