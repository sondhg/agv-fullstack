# Generated by Django 5.1.7 on 2025-04-13 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_generate', '0008_rename_instruction_set_schedule_initial_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='residual_path',
            field=models.TextField(default='[]'),
        ),
    ]
