# Generated by Django 3.2.9 on 2023-03-30 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0037_update_aktivitetskoder'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprodukttype',
            name='g69_use_aktivitetskode_as_fiskeartskode',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='produkttype',
            name='g69_use_aktivitetskode_as_fiskeartskode',
            field=models.BooleanField(default=False),
        ),
    ]