# Generated by Django 4.1 on 2022-09-04 15:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snap_analyzer_django', '0012_rename_name_node_id_1_enclosuremodel_id_node_left_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='enclosuremodel',
            old_name='node_id_1_WWNN',
            new_name='node_left_WWNN',
        ),
        migrations.RenameField(
            model_name='enclosuremodel',
            old_name='service_IP_address_node_id_1',
            new_name='service_IP_address_node_left',
        ),
        migrations.RenameField(
            model_name='enclosuremodel',
            old_name='status_node_id_1',
            new_name='status_node_left',
        ),
    ]
