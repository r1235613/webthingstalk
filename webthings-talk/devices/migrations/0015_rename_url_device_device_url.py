# Generated by Django 3.2.12 on 2022-04-07 17:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0014_remove_device_href'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='url',
            new_name='device_url',
        ),
    ]