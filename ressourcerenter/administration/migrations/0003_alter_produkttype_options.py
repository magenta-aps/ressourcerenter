# Generated by Django 3.2.9 on 2021-12-22 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='produkttype',
            options={'ordering': ['navn_dk']},
        ),
    ]
