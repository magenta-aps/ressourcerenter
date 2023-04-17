from django.db import migrations


def apply_migration(apps, schema_editor):
    ProduktType = apps.get_model("administration", "ProduktType")
    ProduktType.objects.filter(fiskeart__navn_dk="Hellefisk - Indhandling fra havgående").update(
        aktivitetskode_indhandling=10011,
    )
    ProduktType.objects.filter(fiskeart__navn_dk="Hellefisk - Indhandling fra kystnært").update(
        aktivitetskode_indhandling=10012,
    )


def revert_migration(apps, schema_editor):
    ProduktType = apps.get_model("administration", "ProduktType")
    ProduktType.objects.filter(fiskeart__navn_dk="Hellefisk - Indhandling fra havgående").update(
        aktivitetskode_indhandling=10013,
    )
    ProduktType.objects.filter(fiskeart__navn_dk="Hellefisk - Indhandling fra kystnært").update(
        aktivitetskode_indhandling=10013,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0041_hellefisk'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=revert_migration)
    ]
