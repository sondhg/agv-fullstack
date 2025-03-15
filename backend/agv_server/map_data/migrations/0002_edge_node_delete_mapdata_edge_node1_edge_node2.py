# Generated by Django 5.1.7 on 2025-03-15 11:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map_data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.FloatField()),
                ('direction', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True)),
            ],
        ),
        migrations.DeleteModel(
            name='MapData',
        ),
        migrations.AddField(
            model_name='edge',
            name='node1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edge1', to='map_data.node'),
        ),
        migrations.AddField(
            model_name='edge',
            name='node2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edge2', to='map_data.node'),
        ),
    ]
