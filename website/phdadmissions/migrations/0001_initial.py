# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('registry_ref', models.CharField(validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only digits are allowed.')], max_length=100)),
                ('surname', models.CharField(max_length=100)),
                ('forename', models.CharField(max_length=100)),
                ('possible_funding', models.CharField(choices=[('SELF', 'Self'), ('DTP', 'DTP'), ('CDT', 'CDT'), ('PROJECT', 'Project'), ('XSCHOLARSHIP', 'X-Scholarship'), ('DOC', 'DoC'), ('OTHER', 'Other')], max_length=100)),
                ('funding_status', models.CharField(choices=[('PENDING', 'Pending'), ('AWARDED', 'Awarded')], max_length=100, default='PENDING')),
                ('origin', models.CharField(choices=[('HOME', 'Home'), ('EU', 'EU'), ('OVERSEAS', 'Overseas'), ('QUERY', 'Query')], max_length=100)),
                ('student_type', models.CharField(choices=[('COMPUTING', 'Computing'), ('CDT', 'CDT Student Type'), ('COMPUTING_AND_CDT', 'Both Computing and CDT student')], max_length=100)),
                ('status', models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected'), ('REJECT_TO_MSC', 'Rejected to MSc'), ('WITHDRAWN', 'Withdrawn')], max_length=100, default='PENDING')),
                ('research_subject', models.CharField(blank=True, max_length=255, null=True)),
                ('registry_comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supervision',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('acceptance_condition', models.TextField(null=True)),
                ('recommendation', models.CharField(blank=True, choices=[('NOT_VIEWED', 'Not viewed'), ('WAIT_TO_INTERVIEW', 'Wait to interview'), ('REJECT_TO_MSC', 'Reject to MSc'), ('REJECT_TO_MAC', 'Reject to MAC'), ('STRAIGHT_REJECT', 'Straight reject'), ('ACCEPT_BUT_NOT_SUPERVISED', 'Accept but not supervised'), ('ACCEPT_AND_SUPERVISED', 'Accept and supervised'), ('OTHER', 'Other')], max_length=100, default='NOT_VIEWED')),
                ('type', models.CharField(choices=[('ADMIN', 'Administrator'), ('SUPERVISOR', 'Supervisor'), ('SUPER_ADMIN', 'Super Administrator')], max_length=100, default='SUPERVISOR')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('application', models.ForeignKey(related_name='supervisions', to='phdadmissions.Application')),
                ('supervisor', models.OneToOneField(related_name='supervision', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='supervision',
            field=models.ForeignKey(related_name='comments', to='phdadmissions.Supervision'),
        ),
    ]
