# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-07-14 07:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('peer_review', '0029_auto_20170307_1459'),
    ]

    operations = [
        migrations.RenameField(
            model_name='response',
            old_name='batchid',
            new_name='batch_id',
        ),
    ]
