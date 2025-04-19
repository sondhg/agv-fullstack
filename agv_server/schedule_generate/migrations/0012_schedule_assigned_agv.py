# Generated by Django 5.1.7 on 2025-04-19 08:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agv_data', '0004_alter_agv_current_node'),
        ('schedule_generate', '0011_alter_schedule_initial_path_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='assigned_agv',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='agv_data.agv'),
        ),
    ]
