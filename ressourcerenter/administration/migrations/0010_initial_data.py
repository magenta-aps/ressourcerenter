from django.db import migrations
from django.utils import timezone

from project.dateutil import quarter_first_date, quarter_last_date


def apply_migration(apps, schema_editor):
    create_skematyper(apps)
    create_fiskearter(apps)
    create_produkttyper(apps)
    create_afgiftsperioder(apps)
    populate_satstabeller(apps)


def create_skematyper(apps):
    SkemaType = apps.get_model('administration', 'SkemaType')
    if not SkemaType.objects.exists():
        for id, navn in [
            (1, "Havgående fartøjer og kystnære rejefartøjer - producerende fartøjer"),
            (2, "Indhandlinger - Indberetninger fra fabrikkerne / Havgående fiskeri og kystnært fiskeri efter rejer"),
            (3, "Kystnært fiskeri efter andre arter end rejer - indberetninger fra fabrikkerne"),
        ]:
            SkemaType.objects.get_or_create(id=id, navn_dk=navn, navn_gl=navn)


def get_skematype(apps, id):
    return apps.get_model('administration', 'SkemaType').objects.get(id=id)


def create_fiskeart(apps, navn_dk, navn_gl, pelagisk, skematype_ids):
    FiskeArt = apps.get_model('administration', 'FiskeArt')
    fiskeart, _ = FiskeArt.objects.update_or_create(
        navn_dk=navn_dk,
        defaults={
            'navn_gl': navn_gl,
            'pelagisk': pelagisk,
        }
    )
    fiskeart.skematype.set([get_skematype(apps, id) for id in skematype_ids])
    fiskeart.save()
    return fiskeart


def create_produkttype(apps, fiskeart, navn_dk, navn_gl, fartoej_groenlandsk=None, gruppe=None, aktivitetskode_alle=None, **kwargs):
    ProduktType = apps.get_model('administration', 'ProduktType')
    if aktivitetskode_alle is not None:
        kwargs.update({'aktivitetskode_havgående': aktivitetskode_alle, 'aktivitetskode_indhandling': aktivitetskode_alle, 'aktivitetskode_kystnært': aktivitetskode_alle})

    produkttype, _ = ProduktType.objects.update_or_create(
        fiskeart=fiskeart,
        navn_dk=navn_dk,
        fartoej_groenlandsk=fartoej_groenlandsk,
        defaults={
            'navn_gl': navn_gl,
            'gruppe': gruppe,
            **kwargs
        }
    )
    return produkttype


def create_produkttype_subtype(apps, parent, navn_dk, navn_gl):
    create_produkttype(
        apps,
        parent.fiskeart,
        ' - '.join([parent.navn_dk, navn_dk]),
        ' - '.join([parent.navn_gl, navn_gl]),
        gruppe=parent,
    )


def create_fiskearter(apps):
    create_fiskeart(apps, 'Makrel', 'Makrel', True, [1, 2])
    create_fiskeart(apps, 'Sild', 'Sild', True, [1, 2])
    create_fiskeart(apps, 'Lodde', 'Lodde', True, [1, 2])
    create_fiskeart(apps, 'Blåhvilling', 'Blåhvilling', True, [1, 2])
    create_fiskeart(apps, 'Guldlaks', 'Guldlaks', True, [1, 2])
    create_fiskeart(apps, 'Hellefisk', 'Hellefisk', False, [1, 2, 3])
    create_fiskeart(apps, 'Torsk', 'Torsk', False, [1, 2])
    create_fiskeart(apps, 'Kuller', 'Kuller', False, [1, 2])
    create_fiskeart(apps, 'Sej', 'Sej', False, [1, 2])
    create_fiskeart(apps, 'Rødfisk', 'Rødfisk', False, [1, 2])
    create_fiskeart(apps, 'Reje - havgående licens', 'Reje - havgående licens', False, [1, 2])
    create_fiskeart(apps, 'Reje - kystnær licens', 'Reje - kystnær licens', False, [1, 2])
    create_fiskeart(apps, 'Reje - Svalbard og Barentshavet', 'Reje - Svalbard og Barentshavet', False, [1, 2])


def create_produkttyper(apps):

    FiskeArt = apps.get_model('administration', 'FiskeArt')
    makrel = FiskeArt.objects.get(navn_dk='Makrel')
    create_produkttype(
        apps,
        makrel,
        f"{makrel.navn_dk}, grønlandsk fartøj", f"{makrel.navn_gl}, grønlandsk fartøj",
        fartoej_groenlandsk=True,
        aktivitetskode_alle=10021,
    )
    create_produkttype(
        apps,
        makrel,
        f"{makrel.navn_dk}, ikke-grønlandsk fartøj", f"{makrel.navn_gl}, ikke-grønlandsk fartøj",
        fartoej_groenlandsk=False,
        aktivitetskode_alle=10022,
    )

    sild = FiskeArt.objects.get(navn_dk='Sild')
    create_produkttype(
        apps,
        sild,
        f"{sild.navn_dk}, grønlandsk fartøj", f"{sild.navn_gl}, grønlandsk fartøj",
        fartoej_groenlandsk=True,
        aktivitetskode_alle=10023,
    )
    create_produkttype(
        apps,
        sild,
        f"{sild.navn_dk}, ikke-grønlandsk fartøj", f"{sild.navn_gl}, ikke-grønlandsk fartøj",
        fartoej_groenlandsk=False,
        aktivitetskode_alle=10024
    )

    lodde = FiskeArt.objects.get(navn_dk='Lodde')
    create_produkttype(
        apps,
        lodde,
        f"{lodde.navn_dk}, grønlandsk fartøj", f"{lodde.navn_gl}, grønlandsk fartøj",
        fartoej_groenlandsk=True,
        aktivitetskode_alle=10025
    )
    create_produkttype(
        apps,
        lodde,
        f"{lodde.navn_dk}, ikke-grønlandsk fartøj", f"{lodde.navn_gl}, ikke-grønlandsk fartøj",
        fartoej_groenlandsk=False,
        aktivitetskode_alle=10026
    )

    blåhvilling = FiskeArt.objects.get(navn_dk='Blåhvilling')
    create_produkttype(
        apps,
        blåhvilling,
        f"{blåhvilling.navn_dk}, grønlandsk fartøj", f"{blåhvilling.navn_gl}, grønlandsk fartøj",
        fartoej_groenlandsk=True,
        aktivitetskode_alle=10038
    )
    create_produkttype(
        apps,
        blåhvilling,
        f"{blåhvilling.navn_dk}, ikke-grønlandsk fartøj", f"{blåhvilling.navn_gl}, ikke-grønlandsk fartøj",
        fartoej_groenlandsk=False,
        aktivitetskode_alle=10039
    )

    guldlaks = FiskeArt.objects.get(navn_dk='Guldlaks')
    create_produkttype(
        apps,
        guldlaks,
        f"{guldlaks.navn_dk}, grønlandsk fartøj", f"{guldlaks.navn_gl}, grønlandsk fartøj",
        fartoej_groenlandsk=True,
        aktivitetskode_alle=10040
    )
    create_produkttype(
        apps,
        guldlaks,
        f"{guldlaks.navn_dk}, ikke-grønlandsk fartøj", f"{guldlaks.navn_gl}, ikke-grønlandsk fartøj",
        fartoej_groenlandsk=False,
        aktivitetskode_alle=10041
    )

    hellefisk = FiskeArt.objects.get(navn_dk='Hellefisk')
    hellefisk_produkt = create_produkttype(
        apps,
        hellefisk,
        hellefisk.navn_dk, hellefisk.navn_gl,
        aktivitetskode_havgående=10011,
        aktivitetskode_kystnært=10012,
        aktivitetskode_indhandling=10013,
    )
    create_produkttype_subtype(apps, hellefisk_produkt, 'Hel fisk', 'Hel fisk')
    create_produkttype_subtype(apps, hellefisk_produkt, 'Filet', 'Filet')
    create_produkttype_subtype(apps, hellefisk_produkt, 'Biprodukter', 'Biprodukter')

    torsk = FiskeArt.objects.get(navn_dk='Torsk')
    torsk_produkt = create_produkttype(
        apps,
        torsk,
        torsk.navn_dk, torsk.navn_gl,
        aktivitetskode_havgående=10027,
        aktivitetskode_indhandling=10028,
    )
    create_produkttype_subtype(apps, torsk_produkt, 'Hel fisk', 'Hel fisk')
    create_produkttype_subtype(apps, torsk_produkt, 'Filet', 'Filet')
    create_produkttype_subtype(apps, torsk_produkt, 'Biprodukter', 'Biprodukter')

    kuller = FiskeArt.objects.get(navn_dk='Kuller')
    kuller_produkt = create_produkttype(
        apps,
        kuller,
        kuller.navn_dk, kuller.navn_gl,
        aktivitetskode_havgående=10031,
        aktivitetskode_indhandling=10032
    )
    create_produkttype_subtype(apps, kuller_produkt, 'Hel fisk', 'Hel fisk')
    create_produkttype_subtype(apps, kuller_produkt, 'Filet', 'Filet')
    create_produkttype_subtype(apps, kuller_produkt, 'Biprodukter', 'Biprodukter')

    sej = FiskeArt.objects.get(navn_dk='Sej')
    sej_produkt = create_produkttype(
        apps,
        sej,
        sej.navn_dk, sej.navn_gl,
        aktivitetskode_havgående=10033,
        aktivitetskode_indhandling=10034
    )
    create_produkttype_subtype(apps, sej_produkt, 'Hel fisk', 'Hel fisk')
    create_produkttype_subtype(apps, sej_produkt, 'Filet', 'Filet')
    create_produkttype_subtype(apps, sej_produkt, 'Biprodukter', 'Biprodukter')

    rødfisk = FiskeArt.objects.get(navn_dk='Rødfisk')
    rødfisk_produkt = create_produkttype(
        apps,
        rødfisk,
        rødfisk.navn_dk, rødfisk.navn_gl,
        aktivitetskode_havgående=10029,
        aktivitetskode_indhandling=10030,
    )
    create_produkttype_subtype(apps, rødfisk_produkt, 'Hel fisk', 'Hel fisk')
    create_produkttype_subtype(apps, rødfisk_produkt, 'Filet', 'Filet')
    create_produkttype_subtype(apps, rødfisk_produkt, 'Biprodukter', 'Biprodukter')

    reje_havgående = FiskeArt.objects.get(navn_dk='Reje - havgående licens')
    reje_havgående_produkt = create_produkttype(
        apps,
        reje_havgående,
        reje_havgående.navn_dk, reje_havgående.navn_gl,
        aktivitetskode_havgående=10011,
        fangsttype='havgående',
    )
    create_produkttype_subtype(apps, reje_havgående_produkt, 'Råfrosne skalrejer', 'Råfrosne skalrejer')
    create_produkttype_subtype(apps, reje_havgående_produkt, 'Søkogte skalrejer', 'Søkogte skalrejer')
    create_produkttype_subtype(apps, reje_havgående_produkt, 'Industrirejer-sækkerejer', 'Industrirejer-sækkerejer')
    create_produkttype_subtype(apps, reje_havgående_produkt, 'Biprodukter', 'Biprodukter')

    reje_kystnært = FiskeArt.objects.get(navn_dk='Reje - kystnær licens')
    reje_kystnært_produkt = create_produkttype(
        apps,
        reje_kystnært,
        reje_kystnært.navn_dk, reje_kystnært.navn_gl,
        aktivitetskode_kystnært=10012,
        fangsttype='kystnært',
    )
    create_produkttype_subtype(apps, reje_kystnært_produkt, 'Råfrosne skalrejer', 'Råfrosne skalrejer')
    create_produkttype_subtype(apps, reje_kystnært_produkt, 'Søkogte skalrejer', 'Søkogte skalrejer')
    create_produkttype_subtype(apps, reje_kystnært_produkt, 'Industrirejer-sækkerejer', 'Industrirejer-sækkerejer')
    create_produkttype_subtype(apps, reje_kystnært_produkt, 'Biprodukter', 'Biprodukter')

    reje_svalbard = FiskeArt.objects.get(navn_dk='Reje - Svalbard og Barentshavet')
    reje_svalbard_produkt = create_produkttype(
        apps,
        reje_svalbard,
        reje_svalbard.navn_dk, reje_svalbard.navn_gl,
        aktivitetskode_svalbard=10014,
        fangsttype='svalbard',
    )
    create_produkttype_subtype(apps, reje_svalbard_produkt, 'Råfrosne skalrejer', 'Råfrosne skalrejer')
    create_produkttype_subtype(apps, reje_svalbard_produkt, 'Søkogte skalrejer', 'Søkogte skalrejer')
    create_produkttype_subtype(apps, reje_svalbard_produkt, 'Industrirejer-sækkerejer', 'Industrirejer-sækkerejer')
    create_produkttype_subtype(apps, reje_svalbard_produkt, 'Biprodukter', 'Biprodukter')


def create_afgiftsperioder(apps):

    Afgiftsperiode = apps.get_model('administration', 'Afgiftsperiode')
    perioder = []
    if not Afgiftsperiode.objects.exists():
        today = timezone.now().date()
        for year in (2020, 2021, 2022):
            for kvartal, startmonth in ((1, 1), (2, 4), (3, 7), (4, 10)):
                startdate = quarter_first_date(year, kvartal)
                if startdate < today:
                    periode, _ = Afgiftsperiode.objects.get_or_create(
                        navn_dk=f"{kvartal}. kvartal {year}",
                        defaults={
                            'navn_gl': f"1. kvartal {year}",
                            'dato_fra': startdate,
                            'dato_til': quarter_last_date(year, kvartal),
                            'vis_i_indberetning': True
                        }
                    )
                    perioder.append(periode)


def populate_satstabeller(apps):
    FiskeArt = apps.get_model('administration', 'FiskeArt')
    Afgiftsperiode = apps.get_model('administration', 'Afgiftsperiode')
    SatsTabelElement = apps.get_model('administration', 'SatsTabelElement')
    for navn, skematype_id, fartoej_groenlandsk, rate_procent, rate_pr_kg in [
        ('Reje - havgående licens', 1, None, 5, None),
        ('Reje - kystnær licens', 1, None, 5, None),
        ('Reje - Svalbard og Barentshavet', 1, None, 5, None),
        ('Hellefisk', 1, None, 5, None),
        ('Torsk', 1, None, 5, None),
        ('Kuller', 1, None, 5, None),
        ('Sej', 1, None, 5, None),
        ('Rødfisk', 1, None, 5, None),
        ('Sild', 1, True, None, 0.25),
        ('Sild', 1, False, None, 0.8),
        ('Lodde', 1, True, None, 0.15),
        ('Lodde', 1, False, None, 0.7),
        ('Makrel', 1, True, None, 0.4),
        ('Makrel', 1, False, None, 1),
        ('Blåhvilling', 1, True, None, 0.15),
        ('Blåhvilling', 1, False, None, 0.7),
        ('Guldlaks', 1, True, None, 0.15),
        ('Guldlaks', 1, False, None, 0.7),

        ('Reje - havgående licens', 2, None, 5, None),
        ('Reje - kystnær licens', 2, None, 5, None),
        ('Reje - Svalbard og Barentshavet', 2, None, 5, None),
        ('Hellefisk', 2, None, 5, None),
        ('Torsk', 2, None, 5, None),
        ('Kuller', 2, None, 5, None),
        ('Sej', 2, None, 5, None),
        ('Rødfisk', 2, None, 5, None),
        ('Sild', 2, True, None, 0.25),
        ('Sild', 2, False, None, 0.8),
        ('Lodde', 2, True, None, 0.15),
        ('Lodde', 2, False, None, 0.7),
        ('Makrel', 2, True, None, 0.4),
        ('Makrel', 2, False, None, 1),
        ('Blåhvilling', 2, True, None, 0.15),
        ('Blåhvilling', 2, False, None, 0.7),
        ('Guldlaks', 2, True, None, 0.15),
        ('Guldlaks', 2, False, None, 0.7),

        ('Hellefisk', 3, None, 5, None),
        # ('Torsk', 3, None, 5, None),
        # ('Kuller', 3, None, 5, None),
        # ('Sej', 3, None, 5, None),
        # ('Rødfisk', 3, None, 5, None),
    ]:
        fiskeart = FiskeArt.objects.get(navn_dk=navn)
        for periode in Afgiftsperiode.objects.all():
            sats, _ = SatsTabelElement.objects.get_or_create(
                periode=periode,
                skematype=get_skematype(apps, skematype_id),
                fiskeart=fiskeart,
                fartoej_groenlandsk=fartoej_groenlandsk,
            )
            sats.rate_procent = rate_procent
            sats.rate_pr_kg = rate_pr_kg
            sats.save()


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0009_g69codeexport'),
        ('administration', '0010_auto_20220420_0815'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
