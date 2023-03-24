from django.db import migrations


def apply_migration(apps, schema_editor):
    Fiskeart = apps.get_model('administration', 'Fiskeart')
    Fiskeart.objects.filter(navn_dk__startswith="Hellefisk").update(betalingsart=481)
    Fiskeart.objects.filter(navn_dk__startswith="Makrel").update(betalingsart=482)
    Fiskeart.objects.filter(navn_dk__startswith="Sild").update(betalingsart=483)
    Fiskeart.objects.filter(navn_dk__startswith="Lodde").update(betalingsart=484)
    Fiskeart.objects.filter(navn_dk__startswith="Torsk").update(betalingsart=485)
    Fiskeart.objects.filter(navn_dk__startswith="Kuller").update(betalingsart=486)
    Fiskeart.objects.filter(navn_dk__startswith="Sej").update(betalingsart=487)
    Fiskeart.objects.filter(navn_dk__startswith="Rødfisk").update(betalingsart=488)
    Fiskeart.objects.filter(navn_dk__startswith="Reje").update(betalingsart=489)
    Fiskeart.objects.filter(navn_dk__startswith="Blåhvilling").update(betalingsart=492)
    Fiskeart.objects.filter(navn_dk__startswith="Guldlaks").update(betalingsart=493)


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0034_auto_20230323_1721'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
