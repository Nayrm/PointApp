# Generated by Django 4.2.7 on 2024-01-13 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pointqueapp', '0005_alter_pointpiece_associate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointpiece',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
