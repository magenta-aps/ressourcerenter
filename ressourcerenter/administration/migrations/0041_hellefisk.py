from django.db import migrations


def apply_migration(apps, schema_editor):
    FiskeArt = apps.get_model("administration", "FiskeArt")
    FiskeArt.objects.filter(navn_dk__startswith="Hellefisk").update(betalingsart=481)


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0040_hellefisk'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
