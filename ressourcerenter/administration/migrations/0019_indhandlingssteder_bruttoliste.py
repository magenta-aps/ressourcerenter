from django.db import migrations

stedkoder = (
    10000, 10200, 10300, 10301, 10302, 10303, 10304, 10305, 10306, 10309, 10311, 10313, 10314, 10315, 10316,
    10317, 10318, 10319, 10321, 10322, 10323, 10324, 10325, 10326, 10327, 10329, 10332, 10333, 10335, 10400,
    10440, 10441, 10453, 10456, 10462, 10463, 10464, 10465, 10466, 10467, 10469, 10480, 10481, 10482, 10483,
    10484, 10485, 10487, 10488, 10489, 10490, 10491, 10492, 10496, 10500, 10572, 10581, 10582, 10600, 10604,
    10642, 10643, 10695, 10696, 10698, 10724, 10751, 10756, 10757, 10758, 10761, 10762, 10764, 10768, 10771,
    10772, 10773, 10774, 10776, 10777, 19000, 19023, 19078, 19095, 20000, 30000, 40000, 50000, 100000, 110000,
    120000,
)


def apply_migration(apps, schema_editor):
    Indhandlingssted = apps.get_model('indberetning', 'Indhandlingssted')
    Indhandlingssted.objects.filter(stedkode__in=stedkoder).update(aktiv_til_indhandling=True)


def revert_migration(apps, schema_editor):
    Indhandlingssted = apps.get_model('indberetning', 'Indhandlingssted')
    Indhandlingssted.objects.filter(stedkode__in=stedkoder).update(aktiv_til_indhandling=False)


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0018_skematype3_disabled'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=revert_migration)
    ]
