# Generated by Django 3.2.9 on 2021-11-23 15:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administration', '0002_fangstafgift_indberetninglinje'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalFiskeArt',
            fields=[
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4)),
                ('navn', models.TextField(db_index=True)),
                ('beskrivelse', models.TextField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical fiske art',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalAfgiftsperiode',
            fields=[
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4)),
                ('navn', models.TextField(default='')),
                ('vis_i_indberetning', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('dato_fra', models.DateField()),
                ('dato_til', models.DateField()),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical afgiftsperiode',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AlterField(
            model_name='fangsttype',
            name='beskrivelse',
            field=models.TextField(blank=True, default='', verbose_name='Beskrivelse'),
        ),
        migrations.AlterField(
            model_name='fangsttype',
            name='navn',
            field=models.TextField(max_length=2048, verbose_name='Navn'),
        ),
        migrations.AlterField(
            model_name='satstabelelement',
            name='rate_pr_kg_export',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Eksport, kr/kg'),
        ),
        migrations.AlterField(
            model_name='satstabelelement',
            name='rate_pr_kg_indhandling',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Indhandling, kr/kg'),
        ),
        migrations.AlterField(
            model_name='satstabelelement',
            name='rate_prkg_groenland',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Grønlandsk fartøj, kr/kg'),
        ),
        migrations.AlterField(
            model_name='satstabelelement',
            name='rate_prkg_udenlandsk',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Udenlandsk fartøj, kr/kg'),
        ),
        migrations.AlterField(
            model_name='satstabelelement',
            name='rate_procent_export',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Eksport, procent af salgspris'),
        ),
        migrations.AlterField(
            model_name='satstabelelement',
            name='rate_procent_indhandling',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Indhandling, procent af salgspris'),
        ),
        migrations.CreateModel(
            name='HistoricalSatsTabelElement',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('rate_pr_kg_indhandling', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Indhandling, kr/kg')),
                ('rate_pr_kg_export', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Eksport, kr/kg')),
                ('rate_procent_indhandling', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Indhandling, procent af salgspris')),
                ('rate_procent_export', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Eksport, procent af salgspris')),
                ('rate_prkg_groenland', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Grønlandsk fartøj, kr/kg')),
                ('rate_prkg_udenlandsk', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, verbose_name='Udenlandsk fartøj, kr/kg')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('ressource', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='administration.ressource')),
                ('periode', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='administration.afgiftsperiode')),
            ],
            options={
                'verbose_name': 'historical sats tabel element',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProduktKategori',
            fields=[
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4)),
                ('navn', models.TextField(db_index=True)),
                ('beskrivelse', models.TextField(blank=True, default='')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical produkt kategori',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]