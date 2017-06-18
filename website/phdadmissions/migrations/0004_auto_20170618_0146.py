# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0003_application_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='possible_funding',
            field=multiselectfield.db.fields.MultiSelectField(max_length=43, choices=[('SELF', 'Self'), ('DTP', 'DTP'), ('CDT', 'CDT'), ('PROJECT', 'Project'), ('XSCHOLARSHIP', 'X-Scholarship'), ('DOC', 'DoC'), ('OTHER', 'Other')]),
        ),
    ]
