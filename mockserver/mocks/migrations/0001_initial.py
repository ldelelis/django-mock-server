# Generated by Django 2.1.11 on 2019-12-11 23:44

import common.validators
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('content', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Endpoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('path', models.CharField(default='/', max_length=2048, validators=[common.validators.validate_path])),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='mocks.Category')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Header',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('value', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HeaderType',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HttpVerb',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant')),
            ],
            options={
                'verbose_name': 'HTTP Verb',
                'verbose_name_plural': 'HTTP Verbs',
            },
        ),
        migrations.CreateModel(
            name='Mock',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255, serialize=False)),
                ('status_code', models.IntegerField(default=200)),
                ('is_active', models.BooleanField(default=True)),
                ('path', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mocks.Endpoint')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant')),
                ('verb', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mocks.HttpVerb')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Params',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('content', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('mock', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='params', to='mocks.Mock')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant')),
            ],
            options={
                'verbose_name_plural': 'Params',
            },
        ),
        migrations.AddField(
            model_name='header',
            name='header_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mocks.HeaderType'),
        ),
        migrations.AddField(
            model_name='header',
            name='mock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mocks.Mock'),
        ),
        migrations.AddField(
            model_name='header',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant'),
        ),
        migrations.AddField(
            model_name='content',
            name='mock',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='content', to='mocks.Mock'),
        ),
        migrations.AddField(
            model_name='content',
            name='tenant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.Tenant'),
        ),
    ]
