# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-30 23:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('peer_review', '0034_questionlabels'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='QuestionLabels',
            new_name='QuestionLabel',
        ),
    ]
