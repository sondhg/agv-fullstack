# Generated by Django 5.1.7 on 2025-04-19 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule_generate', '0013_alter_schedule_state'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='sp',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='spare_flag',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='state',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='traveling_info',
        ),
        migrations.AlterField(
            model_name='schedule',
            name='cp',
            field=models.JSONField(default=list, help_text='CP: Shared points with other AGVs'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='initial_path',
            field=models.JSONField(default=list, help_text='P_i^j: Path of AGV i performing task j. Once generated, will not change.'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='residual_path',
            field=models.JSONField(default=list, help_text='Pi_i: Remaining points to be visited by AGV i.'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='scp',
            field=models.JSONField(default=list, help_text='SCP: Sequential shared points'),
        ),
    ]
