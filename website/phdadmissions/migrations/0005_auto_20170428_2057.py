# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0004_supervision'),
    ]

    operations = [
        migrations.RenameField(
            model_name='application',
            old_name='modified_date',
            new_name='modified_at',
        ),
        migrations.RenameField(
            model_name='supervision',
            old_name='modified_date',
            new_name='modified_at',
        ),
    ]
