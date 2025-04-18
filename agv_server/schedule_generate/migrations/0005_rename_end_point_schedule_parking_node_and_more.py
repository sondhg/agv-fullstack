# Generated by Django 5.1.7 on 2025-04-06 09:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_generate', '0004_remove_schedule_sequential_shared_points_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='end_point',
            new_name='parking_node',
        ),
        migrations.RenameField(
            model_name='schedule',
            old_name='start_point',
            new_name='storage_node',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='load_amount',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='load_name',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='load_weight',
        ),
        migrations.AddField(
            model_name='schedule',
            name='workstation_node',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
