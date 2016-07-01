# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 13:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('graaftrade', '0004_auto_20160604_1704'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='graaftrade.Broker')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='graaftrade.User')),
            ],
        ),
        migrations.CreateModel(
            name='Chat_Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(default='', max_length=512)),
                ('from_broker', models.BooleanField(default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('chat_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='graaftrade.Chat')),
            ],
        ),
    ]
