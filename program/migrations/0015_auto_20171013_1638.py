# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-10-13 16:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('program', '0014_auto_20171012_1456'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='programslot',
            unique_together=set([]),
        ),
    ]
