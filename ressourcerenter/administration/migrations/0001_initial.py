# Generated by Django 3.2.9 on 2021-11-22 11:52

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Afgiftsperiode',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('navn', models.TextField()),
                ('vis_i_indberetning', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FiskeArt',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('navn', models.TextField(unique=True)),
                ('beskrivelse', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Kategori',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('navn', models.TextField(unique=True)),
                ('beskrivelse', models.TextField()),
            ],
        ),
    ]
