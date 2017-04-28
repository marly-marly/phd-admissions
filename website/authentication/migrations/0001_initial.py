# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(choices=[('admin', 'admin'), ('supervisor', 'supervisor'), ('super_admin', 'super_admin')], max_length=100)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='role')),
            ],
        ),
    ]
