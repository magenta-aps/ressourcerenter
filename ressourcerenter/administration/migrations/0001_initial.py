# Generated by Django 3.2.9 on 2021-11-22 14:12

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Afgiftsperiode',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('navn', models.TextField(default='')),
                ('vis_i_indberetning', models.BooleanField(default=False)),
                ('dato_fra', models.DateField()),
                ('dato_til', models.DateField()),
            ],
            options={'ordering': ['dato_fra', 'dato_til']},
        ),
        migrations.CreateModel(
            name='BeregningsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('navn', models.CharField(max_length=256, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BeregningsModel2021',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beregningsmodel_ptr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.beregningsmodel')),
                ('transport_afgift_rate', models.DecimalField(decimal_places=2, default=None, max_digits=4, null=True, verbose_name='Transportafgift i procent')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FangstType',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('navn', models.TextField(max_length=2048)),
                ('beskrivelse', models.TextField(blank=True, default='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FiskeArt',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('navn', models.TextField(unique=True)),
                ('beskrivelse', models.TextField()),
            ],
            options={
                'ordering': ['navn']
            },
        ),
        migrations.CreateModel(
            name='ProduktKategori',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('navn', models.TextField(unique=True)),
                ('beskrivelse', models.TextField(blank=True, default='')),
            ],
            options={
                'ordering': ['navn']
            },
        ),
        migrations.CreateModel(
            name='Ressource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fangsttype', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.fangsttype')),
                ('fiskeart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.fiskeart')),
            ],
        ),
        migrations.CreateModel(
            name='SatsTabelElement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate_pr_kg_indhandling', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('rate_pr_kg_export', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('rate_procent_indhandling', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('rate_procent_export', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('rate_prkg_groenland', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('rate_prkg_udenlandsk', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('ressource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='administration.ressource')),
                ('periode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='administration.afgiftsperiode')),
            ],
        ),
        migrations.CreateModel(
            name='FangstAfgift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('afgift', models.DecimalField(decimal_places=2, default='0.0', max_digits=12)),
                ('rate_element', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administration.satstabelelement')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='ressource',
            unique_together={('fiskeart', 'fangsttype')},
        ),
        migrations.AlterUniqueTogether(
            name='satstabelelement',
            unique_together={('periode', 'ressource')},
        ),
    ]
