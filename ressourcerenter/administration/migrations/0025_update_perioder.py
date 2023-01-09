from django.db import migrations
from django.utils.translation import gettext as _
from project.dateutil import quarter_first_date, quarter_last_date


def apply_migration(apps, schema_editor):
    update_afgiftsperioder(apps)


def update_afgiftsperioder(apps):

    Afgiftsperiode = apps.get_model('administration', 'Afgiftsperiode')
    for year in (2020, 2021, 2022):
        for kvartal, startmonth in ((1, 1), (2, 4), (3, 7), (4, 10)):
            startdate = quarter_first_date(year, kvartal)
            Afgiftsperiode.objects.filter(
                dato_fra=startdate,
                dato_til=quarter_last_date(year, kvartal),
            ).update(
                navn_gl=str(_("{kvartal}. kvartal {år}")).format(kvartal=kvartal, år=year)
            )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0024_beregningsmodel'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
