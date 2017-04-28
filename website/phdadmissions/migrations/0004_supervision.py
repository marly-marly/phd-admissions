# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('phdadmissions', '0003_auto_20170428_1745'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supervision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('acceptance_condition', models.TextField(null=True)),
                ('recommendation', models.CharField(max_length=100, default='NOT_VIEWED', choices=[('NOT_VIEWED', 'Not viewed'), ('WAIT_TO_INTERVIEW', 'Wait to interview'), ('REJECT_TO_MSC', 'Reject to MSc'), ('REJECT_TO_MAC', 'Reject to MAC'), ('STRAIGHT_REJECT', 'Straight reject'), ('ACCEPT_BUT_NOT_SUPERVISED', 'Accept but not supervised'), ('ACCEPT_AND_SUPERVISED', 'Accept and supervised'), ('OTHER', 'Other')])),
                ('type', models.CharField(max_length=100, default='SUPERVISOR', choices=[('ADMIN', 'Administrator'), ('SUPERVISOR', 'Supervisor'), ('SUPER_ADMIN', 'Super Administrator')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('application', models.ForeignKey(to='phdadmissions.Application', related_name='supervisions')),
                ('supervisor', models.OneToOneField(related_name='supervision', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
