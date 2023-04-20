# Generated by Django 3.2.9 on 2023-03-30 09:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0035_update_10q_betalingsart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalprodukttype',
            name='aktivitetskode_havgående',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(99999)]),
        ),
        migrations.AlterField(
            model_name='historicalprodukttype',
            name='aktivitetskode_indhandling',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(99999)]),
        ),
        migrations.AlterField(
            model_name='historicalprodukttype',
            name='aktivitetskode_kystnært',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(99999)]),
        ),
        migrations.AlterField(
            model_name='produkttype',
            name='aktivitetskode_havgående',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(99999)]),
        ),
        migrations.AlterField(
            model_name='produkttype',
            name='aktivitetskode_indhandling',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(99999)]),
        ),
        migrations.AlterField(
            model_name='produkttype',
            name='aktivitetskode_kystnært',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(99999)]),
        ),
    ]