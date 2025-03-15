# Generated by Django 5.1.7 on 2025-03-15 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map_data', '0002_edge_node_delete_mapdata_edge_node1_edge_node2'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connection_matrix', models.TextField()),
                ('direction_matrix', models.TextField()),
            ],
        ),
        migrations.DeleteModel(
            name='Edge',
        ),
        migrations.DeleteModel(
            name='Node',
        ),
    ]
