from django.db import migrations


def apply_migration(apps, schema_editor):
    FiskeArt = apps.get_model("administration", "FiskeArt")
    FiskeArt.objects.filter(
        navn_dk__in=("Hellefisk - Indhandling fra havgående", "Hellefisk - Indhandling fra kystnært")
    ).update(
        g69_overstyringskode=241125242040197,
    )


def revert_migration(apps, schema_editor):
    FiskeArt = apps.get_model("administration", "FiskeArt")
    FiskeArt.objects.filter(
        navn_dk__in=("Hellefisk - Indhandling fra havgående", "Hellefisk - Indhandling fra kystnært")
    ).update(
        g69_overstyringskode=241126242040197,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0044_fiskenavn_kl'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=revert_migration)
    ]
