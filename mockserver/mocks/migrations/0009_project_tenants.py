# Generated by Django 3.0.5 on 2020-05-31 22:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0010_project_tenants'),
        ('mocks', '0008_endpoint_category_m2m'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tenants.Project'),
        ),
        migrations.AlterField(
            model_name='endpoint',
            name='categories',
            field=models.ManyToManyField(blank=True, null=True, related_name='endpoints', to='mocks.Category'),
        ),
        migrations.DeleteModel(
            name='Project',
        ),
    ]