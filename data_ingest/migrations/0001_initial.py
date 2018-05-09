# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-08 17:53
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('file_metadata', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('file', models.FileField(upload_to='')),
                ('raw', models.BinaryField(null=True)),
                ('validation_results', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('status', models.CharField(choices=[('LOADING', 'Loading'), ('PENDING', 'Pending'), ('STAGED', 'Staged'), ('INSERTED', 'Inserted'), ('DELETED', 'Deleted')], default='LOADING', max_length=10)),
                ('status_changed_at', models.DateTimeField(null=True)),
                ('replaces', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replaced_by', to='data_ingest.DefaultUpload')),
                ('status_changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('submitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
