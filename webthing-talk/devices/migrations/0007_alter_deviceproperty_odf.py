# Generated by Django 3.2.12 on 2022-03-07 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0006_alter_deviceproperty_odf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceproperty',
            name='odf',
            field=models.TextField(blank=True),
        ),
    ]
