# Generated by Django 3.2.9 on 2021-12-14 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('indberetning', '0001_initial'),
        ('administration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fangstafgift',
            name='indberetninglinje',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='indberetning.indberetninglinje'),
        ),
        migrations.AddField(
            model_name='fangstafgift',
            name='rate_element',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='administration.satstabelelement'),
        ),
        migrations.AddField(
            model_name='afgiftsperiode',
            name='beregningsmodel',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='administration.beregningsmodel'),
        ),
        migrations.AlterUniqueTogether(
            name='satstabelelement',
            unique_together={('periode', 'skematype', 'fiskeart', 'fartoej_groenlandsk')},
        ),
        migrations.AlterUniqueTogether(
            name='produkttype',
            unique_together={('fiskeart', 'navn_dk', 'fartoej_groenlandsk')},
        ),
    ]