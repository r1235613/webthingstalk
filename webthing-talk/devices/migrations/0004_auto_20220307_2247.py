# Generated by Django 3.2.12 on 2022-03-07 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_auto_20220307_2247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deviceproperty',
            name='df',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='deviceproperty',
            name='name',
            field=models.TextField(),
        ),
    ]