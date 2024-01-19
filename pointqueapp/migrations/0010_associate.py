# Generated by Django 4.2.7 on 2024-01-16 20:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pointqueapp', '0009_dc_pointpiece_dc'),
    ]

    operations = [
        migrations.CreateModel(
            name='associate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('associate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('dc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pointqueapp.dc')),
            ],
        ),
    ]
