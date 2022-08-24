from django.db import migrations


def apply_migration(apps, schema_editor):
    BeregningsModel2021 = apps.get_model('administration', 'BeregningsModel2021')
    model = BeregningsModel2021.objects.get(
        navn="BeregningsModel2021",
    )
    Afgiftsperiode = apps.get_model('administration', 'Afgiftsperiode')
    Afgiftsperiode.objects.filter(beregningsmodel__isnull=True).update(beregningsmodel=model)


def revert_migration(apps, schema_editor):
    BeregningsModel2021 = apps.get_model('administration', 'BeregningsModel2021')
    model = BeregningsModel2021.objects.get(
        navn="BeregningsModel2021",
    )
    Afgiftsperiode = apps.get_model('administration', 'Afgiftsperiode')
    Afgiftsperiode.objects.filter(beregningsmodel=model).update(beregningsmodel=None)


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0023_remove_beregningsmodel2021_transport_afgift_rate'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=revert_migration)
    ]
