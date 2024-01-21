# Generated by Django 4.2.7 on 2024-01-16 20:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pointqueapp', '0008_parttype_pointpiece_part'),
    ]

    operations = [
        migrations.CreateModel(
            name='DC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dc', models.IntegerField(unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='pointpiece',
            name='dc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pointqueapp.dc'),
        ),
    ]