from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from datetime import date

from administration.models import SkemaType, FiskeArt, ProduktType, Afgiftsperiode


class Command(BaseCommand):
    help = 'Create basic data'

    def handle(self, *args, **options):

        skematyper = {}
        for id, navn in [
            (1, "Havgående fartøjer og kystnære rejefartøjer - producerende fartøjer"),
            (2, "Indhandlinger - Indberetninger fra fabrikkerne / Havgående fiskeri og kystnært fiskeri efter rejer"),
            (3, "Kystnært fiskeri efter andre arter end rejer - indberetninger fra fabrikkerne"),
        ]:
            try:
                skematyper[id] = SkemaType.objects.create(id=id, navn_dk=navn, navn_gl=navn)
            except IntegrityError:
                skematyper[id] = SkemaType.objects.get(id=id)

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
            try:
                fiskeart = FiskeArt.objects.create(navn_dk=navn, navn_gl=navn, pelagisk=pelagisk)
                fiskeart.skematype.set([skematyper[id] for id in skematype])
                fiskeart.save()
            except IntegrityError:
                fiskeart = FiskeArt.objects.get(navn_dk=navn)

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

        for year in (2021, 2022, 2023):
            try:
                Afgiftsperiode.objects.create(navn=f"1. kvartal {year}", dato_fra=date(year, 1, 1), dato_til=date(year, 3, 31), vis_i_indberetning=True)
            except IntegrityError:
                pass
            try:
                Afgiftsperiode.objects.create(navn=f"2. kvartal {year}", dato_fra=date(year, 4, 1), dato_til=date(year, 6, 30), vis_i_indberetning=True)
            except IntegrityError:
                pass
            try:
                Afgiftsperiode.objects.create(navn=f"3. kvartal {year}", dato_fra=date(year, 7, 1), dato_til=date(year, 9, 30), vis_i_indberetning=True)
            except IntegrityError:
                pass
            try:
                Afgiftsperiode.objects.create(navn=f"4. kvartal {year}", dato_fra=date(year, 10, 1), dato_til=date(year, 12, 31), vis_i_indberetning=True)
            except IntegrityError:
                pass
