# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('registry_ref', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only digits are allowed.')])),
                ('surname', models.CharField(max_length=100)),
                ('forename', models.CharField(max_length=100)),
                ('possible_funding', models.CharField(max_length=100, choices=[('SELF', 'Self'), ('DTP', 'DTP'), ('CDT', 'CDT'), ('PROJECT', 'Project'), ('XSCHOLARSHIP', 'X-Scholarship'), ('DOC', 'DoC'), ('OTHER', 'Other')])),
                ('funding_status', models.CharField(max_length=100, choices=[('PENDING', 'Pending'), ('AWARDED', 'Awarded')])),
                ('origin', models.CharField(max_length=100, choices=[('HOME', 'Home'), ('EU', 'EU'), ('OVERSEAS', 'Overseas'), ('QUERY', 'Query')])),
                ('student_type', models.CharField(max_length=100, choices=[('COMPUTING', 'Computing'), ('CDT', 'CDT Student Type'), ('COMPUTING_AND_CDT', 'Both Computing and CDT student')])),
                ('research_subject', models.CharField(null=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
