from django.db import migrations


def apply_migration(apps, schema_editor):
    update_fiskearter(apps)
    update_produkttyper(apps)


def update_fiskearter(apps):

    Fiskeart = apps.get_model('administration', 'Fiskeart')
    Fiskeart.objects.filter(navn_dk="Guldlaks").update(navn_gl="Ammassassuaasat")


def update_produkttyper(apps):

    ProduktType = apps.get_model('administration', 'ProduktType')
    ProduktType.objects.filter(fiskeart__navn_dk="Guldlaks", fartoej_groenlandsk=False).update(navn_gl="Ammassassuaasat, kalaallit angallatiginngisaat")
    ProduktType.objects.filter(fiskeart__navn_dk="Guldlaks", fartoej_groenlandsk=True).update(navn_gl="Ammassassuaasat, kalaallit angallataat")


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0029_update_skematyper'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
