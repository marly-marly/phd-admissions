# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import phdadmissions.models.documentation
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicYear',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=255)),
                ('start_date', models.DateTimeField(null=True)),
                ('end_date', models.DateTimeField(null=True)),
                ('default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('registry_ref', models.CharField(unique=True, validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only digits are allowed.')], max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('surname', models.CharField(max_length=100)),
                ('forename', models.CharField(max_length=100)),
                ('possible_funding', models.CharField(choices=[('SELF', 'Self'), ('DTP', 'DTP'), ('CDT', 'CDT'), ('PROJECT', 'Project'), ('XSCHOLARSHIP', 'X-Scholarship'), ('DOC', 'DoC'), ('OTHER', 'Other')], max_length=100)),
                ('funding_status', models.CharField(default='PENDING', choices=[('PENDING', 'Pending'), ('AWARDED', 'Awarded')], max_length=100)),
                ('origin', models.CharField(choices=[('HOME', 'Home'), ('EU', 'EU'), ('OVERSEAS', 'Overseas'), ('QUERY', 'Query')], max_length=100)),
                ('student_type', models.CharField(choices=[('COMPUTING', 'Computing'), ('CDT', 'CDT Student Type'), ('COMPUTING_AND_CDT', 'Both Computing and CDT student')], max_length=100)),
                ('status', models.CharField(default='PENDING', blank=True, choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('REJECT_TO_MSC', 'Rejected to MSc'), ('WITHDRAWN', 'Withdrawn'), ('DEFERRED', 'Deferred')], max_length=100)),
                ('research_subject', models.CharField(max_length=255, blank=True, null=True)),
                ('registry_comment', models.TextField(blank=True, null=True)),
                ('academic_year', models.ForeignKey(to='phdadmissions.AcademicYear', related_name='applications')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Documentation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('file', models.FileField(upload_to=phdadmissions.models.documentation.content_file_name, null=True)),
                ('file_name', models.CharField(max_length=255, null=True)),
                ('file_type', models.CharField(choices=[('APPLICATION_FORM', 'Application form'), ('RESEARCH_SUMMARY', 'Research summary'), ('REFERENCE', 'Reference'), ('ADDITIONAL_MATERIAL', 'Additional material')], max_length=100)),
                ('description', models.CharField(max_length=255, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supervision',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('acceptance_condition', models.TextField(null=True)),
                ('recommendation', models.CharField(default='NOT_VIEWED', blank=True, choices=[('NOT_VIEWED', 'Not viewed'), ('WAIT_TO_INTERVIEW', 'Wait to interview'), ('REJECT_TO_MSC', 'Reject to MSc'), ('REJECT_TO_MAC', 'Reject to MAC'), ('STRAIGHT_REJECT', 'Straight reject'), ('ACCEPT_BUT_NOT_SUPERVISED', 'Accept but not supervised'), ('ACCEPT_AND_SUPERVISED', 'Accept and supervised'), ('OTHER', 'Other')], max_length=100)),
                ('type', models.CharField(default='SUPERVISOR', choices=[('ADMIN', 'Administrator'), ('SUPERVISOR', 'Supervisor')], max_length=100)),
                ('creator', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('application', models.ForeignKey(to='phdadmissions.Application', related_name='supervisions')),
                ('supervisor', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='supervisions')),
            ],
        ),
        migrations.AddField(
            model_name='documentation',
            name='supervision',
            field=models.ForeignKey(to='phdadmissions.Supervision', related_name='documentations'),
        ),
        migrations.AddField(
            model_name='comment',
            name='supervision',
            field=models.ForeignKey(to='phdadmissions.Supervision', related_name='comments'),
        ),
        migrations.AlterUniqueTogether(
            name='supervision',
            unique_together=set([('application', 'supervisor', 'type')]),
        ),
    ]
