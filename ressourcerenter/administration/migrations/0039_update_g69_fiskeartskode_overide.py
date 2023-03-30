from django.db import migrations


def apply_migration(apps, schema_editor):
    ProduktType = apps.get_model('administration', 'ProduktType')
    FiskeArt = apps.get_model('administration', 'FiskeArt')
    ProduktType.objects.filter(navn_dk__startswith='Reje').update(
        g69_use_aktivitetskode_as_fiskeartskode=True,
    )
    FiskeArt.objects.filter(navn_dk__contains='Svalbard').update(
        kode=14
    )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0038_auto_20230330_1548'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
