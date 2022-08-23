from django.db import migrations

stedkoder = (
    (10200, 'Qaasuitsup Kommunia Fælles'),
    (10300, 'Kommune Kujalleq Fælles'),
    (10301, 'Bygdeområde 1 - Aappilattoq, Narsarmijiit, Tasiusaq'),
    (10302, 'Bygdeområde 2 - Ammassivik/Qallumiut, Alluitsup paa'),
    (10303, 'Bygdeområde 3 - Saarloq, Eqalugaarsuit, Qassimiut'),
    (10304, 'Bygdeområde 4 - Qassiarsuk, Narsarsuaq, Igaliko'),
    (10400, 'Kommuneqarfik Sermersooq Fælles'),
    (10500, 'Qeqqata Kommunia Fælles'),
    (10600, 'Kommune Qeqertalik Fælles'),
    (19000, 'Udenfor kommuneinddeling'),
    (10700, 'Avannaata Kommunia'),
    (10000, 'Grønland'),
    (20000, 'Danmark'),
    (30000, 'Færøerne'),
    (40000, 'Island'),
    (50000, 'Norge'),
    (100000, 'Belgien'),
    (110000, 'Holland'),
    (120000, 'Storbritannien'),
)


def apply_migration(apps, schema_editor):
    Indberetning = apps.get_model('indberetning', 'Indberetning')
    Indberetning.objects.filter(virksomhed__sted__stedkode__in=[kode[0] for kode in stedkoder]).delete()
    Virksomhed = apps.get_model('indberetning', 'Virksomhed')
    Virksomhed.objects.filter(sted__stedkode__in=[kode[0] for kode in stedkoder]).delete()
    Indhandlingssted = apps.get_model('indberetning', 'Indhandlingssted')
    Indhandlingssted.objects.filter(stedkode__in=[kode[0] for kode in stedkoder]).delete()


def revert_migration(apps, schema_editor):
    Indhandlingssted = apps.get_model('indberetning', 'Indhandlingssted')
    for stedkode, navn in stedkoder:
        Indhandlingssted.objects.create(
            stedkode=stedkode,
            navn=navn,
            aktiv_til_indhandling=False,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0020_indhandlingssteder'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=revert_migration)
    ]
