# Generated by Django 5.1.7 on 2025-04-06 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_generate', '0005_rename_end_point_schedule_parking_node_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='cp',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='schedule',
            name='scp',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='schedule',
            name='sp',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='schedule',
            name='spare_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='schedule',
            name='state',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='schedule',
            name='traveling_info',
            field=models.JSONField(default=dict),
        ),
    ]
