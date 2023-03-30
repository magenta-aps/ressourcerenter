from django.db import migrations


def apply_migration(apps, schema_editor):
    ProduktType = apps.get_model('administration', 'ProduktType')
    ProduktType.objects.filter(navn_dk__startswith='Reje').update(
        aktivitetskode_indhandling=10012,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0036_auto_20230330_1157'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
