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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(choices=[('SUPER_ADMIN', 'SUPER_ADMIN'), ('ADMIN', 'ADMIN'), ('SUPERVISOR', 'SUPERVISOR')], max_length=100)),
                ('user', models.OneToOneField(related_name='role', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
