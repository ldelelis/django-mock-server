# Generated by Django 2.1.7 on 2019-03-29 15:01

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, validators=[core.validators.validate_path])),
                ('verb', models.CharField(default='GET', max_length=20)),
                ('content', models.TextField(validators=[core.validators.validate_json])),
                ('status_code', models.IntegerField(default=200)),
            ],
        ),
    ]
