# Generated by Django 3.2.9 on 2021-12-22 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indberetning', '0002_indberetninglinje_kommentar'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='indberetninglinje',
            options={'ordering': ('produkttype__navn_dk',)},
        ),
    ]
