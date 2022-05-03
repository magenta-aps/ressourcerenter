from django.db import migrations
from django.db.models import Max


def get_aktivitetskode(produkttype, fangsttype):
    if fangsttype == 'havgående':
        kode = produkttype.aktivitetskode_havgående
    elif fangsttype == 'indhandling':
        kode = produkttype.aktivitetskode_indhandling
    elif fangsttype == 'kystnært':
        kode = produkttype.aktivitetskode_kystnært
    elif fangsttype == 'svalbard':
        kode = produkttype.aktivitetskode_svalbard
    else:
        kode = None
    if kode is None and produkttype.gruppe is not None:
        return get_aktivitetskode(produkttype.gruppe, fangsttype)
    return kode


def apply_migration(apps, schema_editor):

    FiskeArt = apps.get_model('administration', 'FiskeArt')
    current_max = FiskeArt.objects.aggregate(Max('kode'))['kode__max'] or 0
    for fiskeart in FiskeArt.objects.filter(kode__isnull=True):
        current_max += 1
        fiskeart.kode = current_max
        fiskeart.save()

    G69Code = apps.get_model('administration', 'G69Code')
    ProduktType = apps.get_model('administration', 'ProduktType')
    Indhandlingssted = apps.get_model('indberetning', 'Indhandlingssted')
    for år in range(2020, 2025):
        for produkttype in ProduktType.objects.all():
            fangsttyper = filter(None, iter([
                'havgående' if produkttype.aktivitetskode_havgående else None,
                'indhandling' if produkttype.aktivitetskode_indhandling else None,
                'kystnært' if produkttype.aktivitetskode_kystnært else None,
                'svalbard' if produkttype.aktivitetskode_svalbard else None,
            ]))
            for sted in Indhandlingssted.objects.all():
                for fangsttype in fangsttyper:
                    code, _ = G69Code.objects.get_or_create(
                        år=år,
                        produkttype=produkttype,
                        fangsttype=fangsttype,
                        sted=sted
                    )
                    code.kode = (''.join([
                        str(code.år).zfill(2)[-2:],
                        str(code.sted.stedkode)[-5:].zfill(5),
                        str(produkttype.fiskeart.kode).zfill(2),
                        str(get_aktivitetskode(produkttype, fangsttype)).zfill(6),
                    ])).zfill(15)
                    code.save()


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0011_initial_indhandlingssteder'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
