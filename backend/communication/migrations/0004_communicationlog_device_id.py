# Generated by Django 3.1 on 2023-09-13 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0003_auto_20230113_1005'),
    ]

    operations = [
        migrations.AddField(
            model_name='communicationlog',
            name='device_id',
            field=models.CharField(blank=True, help_text='Device ID', max_length=255, null=True),
        ),
    ]
