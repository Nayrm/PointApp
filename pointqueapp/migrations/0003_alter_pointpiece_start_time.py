# Generated by Django 4.2.7 on 2023-12-24 22:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pointqueapp', '0002_pointpiece_lp_pointpiece_route_pointpiece_sku'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointpiece',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
