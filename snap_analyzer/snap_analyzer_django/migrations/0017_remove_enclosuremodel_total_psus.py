# Generated by Django 4.1 on 2022-09-07 15:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('snap_analyzer_django', '0016_enclosuremodel_online_batteries'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enclosuremodel',
            name='total_PSUs',
        ),
    ]