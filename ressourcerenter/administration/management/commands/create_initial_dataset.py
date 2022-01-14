from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from datetime import date

from django.utils import timezone

from administration.models import SkemaType, FiskeArt, ProduktType, Afgiftsperiode, SatsTabelElement


class Command(BaseCommand):
    help = 'Create basic data'

    def handle(self, *args, **options):

        skematyper = {}
        if not SkemaType.objects.exists():
            for id, navn in [
                (1, "Havgående fartøjer og kystnære rejefartøjer - producerende fartøjer"),
                (2, "Indhandlinger - Indberetninger fra fabrikkerne / Havgående fiskeri og kystnært fiskeri efter rejer"),
                (3, "Kystnært fiskeri efter andre arter end rejer - indberetninger fra fabrikkerne"),
            ]:
                skematyper[id] = SkemaType.objects.create(id=id, navn_dk=navn, navn_gl=navn)

        if not FiskeArt.objects.exists():
            for navn, pelagisk, skematype in [
                ('Makrel', True, [1, 2]),
                ('Sild', True, [1, 2]),
                ('Lodde', True, [1, 2]),
                ('Blåhvilling', True, [1, 2]),
                ('Guldlaks', True, [1, 2]),
                ('Hellefisk', False, [1, 2, 3]),
                ('Torsk', False, [1, 2, 3]),
                ('Kuller', False, [1, 2, 3]),
                ('Sej', False, [1, 2, 3]),
                ('Rødfisk', False, [1, 2, 3]),
                ('Reje - havgående licens', False, [1, 2]),
                ('Reje - kystnær licens', False, [1, 2]),
            ]:
                fiskeart = FiskeArt.objects.create(navn_dk=navn, navn_gl=navn, pelagisk=pelagisk)
                fiskeart.skematype.set([skematyper[id] for id in skematype])
                fiskeart.save()

                if fiskeart.pelagisk:
                    # Som det står lige nu, er fartoej_groenlandsk relevant når der er tale om pelagisk fiskeri
                    try:
                        navn_dk = f"{fiskeart.navn_dk}, ikke-grønlandsk fartøj"
                        navn_gl = f"{fiskeart.navn_gl}, ikke-grønlandsk fartøj"
                        ProduktType.objects.create(fiskeart=fiskeart, navn_dk=navn_dk, navn_gl=navn_gl, fartoej_groenlandsk=False)
                    except IntegrityError:
                        pass
                    try:
                        navn_dk = f"{fiskeart.navn_dk}, grønlandsk fartøj"
                        navn_gl = f"{fiskeart.navn_gl}, grønlandsk fartøj"
                        ProduktType.objects.create(fiskeart=fiskeart, navn_dk=navn_dk, navn_gl=navn_gl, fartoej_groenlandsk=True)
                    except IntegrityError:
                        pass
                else:
                    try:
                        ProduktType.objects.create(fiskeart=fiskeart, navn_dk=fiskeart.navn_dk, navn_gl=fiskeart.navn_gl, fartoej_groenlandsk=None)
                    except IntegrityError:
                        pass

        perioder = []
        if not Afgiftsperiode.objects.exists():
            today = timezone.now().date()
            for year in (2020, 2021, 2022):
                try:
                    startdate = date(year, 1, 1)
                    if startdate < today:
                        perioder.append(Afgiftsperiode.objects.create(navn_dk=f"1. kvartal {year}", navn_gl=f"1. kvartal {year}", dato_fra=startdate, dato_til=date(year, 3, 31), vis_i_indberetning=True))
                except IntegrityError:
                    pass
                try:
                    startdate = date(year, 4, 1)
                    if startdate < today:
                        perioder.append(Afgiftsperiode.objects.create(navn_dk=f"2. kvartal {year}", navn_gl=f"2. kvartal {year}", dato_fra=startdate, dato_til=date(year, 6, 30), vis_i_indberetning=True))
                except IntegrityError:
                    pass
                try:
                    startdate = date(year, 7, 1)
                    if startdate < today:
                        perioder.append(Afgiftsperiode.objects.create(navn_dk=f"3. kvartal {year}", navn_gl=f"3. kvartal {year}", dato_fra=startdate, dato_til=date(year, 9, 30), vis_i_indberetning=True))
                except IntegrityError:
                    pass
                try:
                    startdate = date(year, 10, 1)
                    if startdate < today:
                        perioder.append(Afgiftsperiode.objects.create(navn_dk=f"4. kvartal {year}", navn_gl=f"4. kvartal {year}", dato_fra=startdate, dato_til=date(year, 12, 31), vis_i_indberetning=True))
                except IntegrityError:
                    pass

            for navn, skematype_id, fartoej_groenlandsk, rate_procent, rate_pr_kg in [
                ('Reje - havgående licens', 1, None, 5, None),
                ('Reje - kystnær licens', 1, None, 5, None),
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
                ('Torsk', 3, None, 5, None),
                ('Kuller', 3, None, 5, None),
                ('Sej', 3, None, 5, None),
                ('Rødfisk', 3, None, 5, None),
            ]:
                fiskeart = FiskeArt.objects.get(navn_dk=navn)
                for periode in perioder:
                    sats = SatsTabelElement.objects.get(
                        periode=periode,
                        skematype__id=skematype_id,
                        fiskeart=fiskeart,
                        fartoej_groenlandsk=fartoej_groenlandsk,
                    )
                    sats.rate_procent = rate_procent
                    sats.rate_pr_kg = rate_pr_kg
                    sats.save()
