from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('administration', '0001_initial'),
    ]

    def create_resources(apps, schema_editor):
        from administration.models import FiskeArt, FangstType, Ressource

        for fish, place in [
            ('Reje', 'Havgående'),
            ('Reje', 'Kystnært'),
            ('Hellefisk', 'Havgående'),
            ('Hellefisk', 'Kystnært'),
            ('Torsk', 'Havgående'),
            ('Krabbe', 'Havgående'),
            ('Kuller', 'Havgående'),
            ('Sej', 'Havgående'),
            ('Rødfisk', 'Havgående'),
            ('Kammusling', 'Havgående'),
            ('Makrel', 'Havgående'),
            ('Makrel', 'Kystnært'),
            ('Sild', 'Havgående'),
            ('Sild', 'Kystnært'),
            ('Lodde', 'Havgående'),
            ('Lodde', 'Kystnært'),
            ('Blåhvilling', 'Havgående'),
            ('Blåhvilling', 'Kystnært'),
            ('Guldlaks', 'Havgående'),
            ('Guldlaks', 'Kystnært'),
        ]:
            (fiskeart, created) = FiskeArt.objects.get_or_create(navn=fish)
            (fangsttype, created) = FangstType.objects.get_or_create(navn=place)

            Ressource.objects.get_or_create(
                fiskeart=fiskeart,
                fangsttype=fangsttype,
            )

    operations = [
        migrations.RunPython(create_resources),
    ]
