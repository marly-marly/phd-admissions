# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phdadmissions.models.documentation


class Migration(migrations.Migration):

    dependencies = [
        ('phdadmissions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Documentation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('file', models.FileField(null=True, upload_to=phdadmissions.models.documentation.content_file_name)),
                ('file_type', models.CharField(choices=[('APPLICATION_FORM', 'Application form'), ('RESEARCH_SUMMARY', 'Research summary'), ('REFERENCE', 'Reference'), ('ADDITIONAL_MATERIAL', 'Additional material')], max_length=100)),
                ('description', models.CharField(null=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('supervision', models.ForeignKey(to='phdadmissions.Supervision', related_name='documentations')),
            ],
        ),
    ]
