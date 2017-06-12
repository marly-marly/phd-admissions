# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0007_auto_20170611_2221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='academic_year',
            field=models.ForeignKey(to='phdadmissions.AcademicYear', related_name='applications'),
        ),
    ]
