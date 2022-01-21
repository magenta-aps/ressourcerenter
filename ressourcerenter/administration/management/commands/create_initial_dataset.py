from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from datetime import date

from django.utils import timezone

from administration.models import SkemaType, FiskeArt, ProduktType, Afgiftsperiode, SatsTabelElement


class Command(BaseCommand):
    help = 'Create basic data'

    def create_fiskeart(self, navn_dk, navn_gl, pelagisk, skematype_ids):
        try:
            fiskeart = FiskeArt.objects.create(navn_dk=navn_dk, navn_gl=navn_gl, pelagisk=pelagisk)
            fiskeart.skematype.set([self.skematyper[id] for id in skematype_ids])
            fiskeart.save()
        except IntegrityError:
            fiskeart = FiskeArt.objects.get(navn_dk=navn_dk)
        return fiskeart

    def create_produkttype(self, fiskeart, navn_dk, navn_gl, fartoej_groenlandsk=None, gruppe=None):
        try:
            produkttype = ProduktType.objects.create(fiskeart=fiskeart, navn_dk=navn_dk, navn_gl=navn_gl, fartoej_groenlandsk=fartoej_groenlandsk, gruppe=gruppe)
        except IntegrityError:
            produkttype = ProduktType.objects.get(fiskeart=fiskeart, navn_dk=navn_dk, fartoej_groenlandsk=fartoej_groenlandsk)
        return produkttype

    def handle(self, *args, **options):

        self.skematyper = {}
        if not SkemaType.objects.exists():
            for id, navn in [
                (1, "Havgående fartøjer og kystnære rejefartøjer - producerende fartøjer"),
                (2, "Indhandlinger - Indberetninger fra fabrikkerne / Havgående fiskeri og kystnært fiskeri efter rejer"),
                (3, "Kystnært fiskeri efter andre arter end rejer - indberetninger fra fabrikkerne"),
            ]:
                self.skematyper[id] = SkemaType.objects.create(id=id, navn_dk=navn, navn_gl=navn)

        if not FiskeArt.objects.exists():
            makrel = self.create_fiskeart('Makrel', 'Makrel', True, [1, 2])
            sild = self.create_fiskeart('Sild', 'Sild', True, [1, 2])
            lodde = self.create_fiskeart('Lodde', 'Lodde', True, [1, 2])
            blåhvilling = self.create_fiskeart('Blåhvilling', 'Blåhvilling', True, [1, 2])
            guldlaks = self.create_fiskeart('Guldlaks', 'Guldlaks', True, [1, 2])
            hellefisk = self.create_fiskeart('Hellefisk', 'Hellefisk', False, [1, 2, 3])
            torsk = self.create_fiskeart('Torsk', 'Torsk', False, [1, 2])
            kuller = self.create_fiskeart('Kuller', 'Kuller', False, [1, 2])
            sej = self.create_fiskeart('Sej', 'Sej', False, [1, 2])
            rødfisk = self.create_fiskeart('Rødfisk', 'Rødfisk', False, [1, 2])
            reje_havgående = self.create_fiskeart('Reje - havgående licens', 'Reje - havgående licens', False, [1, 2])
            reje_kystnært = self.create_fiskeart('Reje - kystnær licens', 'Reje - kystnær licens', False, [1, 2])

            self.create_produkttype(makrel, f"{makrel.navn_dk}, ikke-grønlandsk fartøj", f"{makrel.navn_gl}, ikke-grønlandsk fartøj", False)
            self.create_produkttype(makrel, f"{makrel.navn_dk}, grønlandsk fartøj", f"{makrel.navn_gl}, grønlandsk fartøj", True)
            self.create_produkttype(sild, f"{sild.navn_dk}, ikke-grønlandsk fartøj", f"{sild.navn_gl}, ikke-grønlandsk fartøj", False)
            self.create_produkttype(sild, f"{sild.navn_dk}, grønlandsk fartøj", f"{sild.navn_gl}, grønlandsk fartøj", True)
            self.create_produkttype(lodde, f"{lodde.navn_dk}, ikke-grønlandsk fartøj", f"{lodde.navn_gl}, ikke-grønlandsk fartøj", False)
            self.create_produkttype(lodde, f"{lodde.navn_dk}, grønlandsk fartøj", f"{lodde.navn_gl}, grønlandsk fartøj", True)
            self.create_produkttype(blåhvilling, f"{blåhvilling.navn_dk}, ikke-grønlandsk fartøj", f"{blåhvilling.navn_gl}, ikke-grønlandsk fartøj", False)
            self.create_produkttype(blåhvilling, f"{blåhvilling.navn_dk}, grønlandsk fartøj", f"{blåhvilling.navn_gl}, grønlandsk fartøj", True)
            self.create_produkttype(guldlaks, f"{guldlaks.navn_dk}, ikke-grønlandsk fartøj", f"{guldlaks.navn_gl}, ikke-grønlandsk fartøj", False)
            self.create_produkttype(guldlaks, f"{guldlaks.navn_dk}, grønlandsk fartøj", f"{guldlaks.navn_gl}, grønlandsk fartøj", True)

            hellefisk_produkt = self.create_produkttype(hellefisk, hellefisk.navn_dk, hellefisk.navn_gl, None)
            self.create_produkttype(hellefisk, 'Hellefisk - Hel fisk', 'Hellefisk - Hel fisk', None, hellefisk_produkt)
            self.create_produkttype(hellefisk, 'Hellefisk - Filet', 'Hellefisk - Filet', None, hellefisk_produkt)
            self.create_produkttype(hellefisk, 'Hellefisk - Biprodukter', 'Hellefisk - Biprodukter', None, hellefisk_produkt)

            torsk_produkt = self.create_produkttype(torsk, torsk.navn_dk, torsk.navn_gl, None)
            self.create_produkttype(torsk, 'Torsk - Hel fisk', 'Torsk - Hel fisk', None, torsk_produkt)
            self.create_produkttype(torsk, 'Torsk - Filet', 'Torsk - Filet', None, torsk_produkt)
            self.create_produkttype(torsk, 'Torsk - Biprodukter', 'Torsk - Biprodukter', None, torsk_produkt)

            kuller_produkt = self.create_produkttype(kuller, kuller.navn_dk, kuller.navn_gl, None)
            self.create_produkttype(kuller, 'Kuller - Hel fisk', 'Kuller - Hel fisk', None, kuller_produkt)
            self.create_produkttype(kuller, 'Kuller - Filet', 'Kuller - Filet', None, kuller_produkt)
            self.create_produkttype(kuller, 'Kuller - Biprodukter', 'Kuller - Biprodukter', None, kuller_produkt)

            sej_produkt = self.create_produkttype(sej, sej.navn_dk, sej.navn_gl, None)
            self.create_produkttype(sej, 'Sej - Hel fisk', 'Sej - Hel fisk', None, sej_produkt)
            self.create_produkttype(sej, 'Sej - Filet', 'Sej - Filet', None, sej_produkt)
            self.create_produkttype(sej, 'Sej - Biprodukter', 'Sej - Biprodukter', None, sej_produkt)

            rødfisk_produkt = self.create_produkttype(rødfisk, rødfisk.navn_dk, rødfisk.navn_gl, None)
            self.create_produkttype(rødfisk, 'Rødfisk - Hel fisk', 'Rødfisk - Hel fisk', None, rødfisk_produkt)
            self.create_produkttype(rødfisk, 'Rødfisk - Filet', 'Rødfisk - Filet', None, rødfisk_produkt)
            self.create_produkttype(rødfisk, 'Rødfisk - Biprodukter', 'Rødfisk - Biprodukter', None, rødfisk_produkt)

            reje_havgående_produkt = self.create_produkttype(reje_havgående, 'Reje - havgående licens', 'Reje - havgående licens', None)
            self.create_produkttype(reje_havgående, 'Reje - havgående licens - Råfrosne skalrejer', 'Reje - havgående licens - Råfrosne skalrejer', None, reje_havgående_produkt)
            self.create_produkttype(reje_havgående, 'Reje - havgående licens - Søkogte skalrejer', 'Reje - havgående licens - Søkogte skalrejer', None, reje_havgående_produkt)
            self.create_produkttype(reje_havgående, 'Reje - havgående licens - Industrirejer-sækkerejer', 'Reje - havgående licens - Industrirejer-sækkerejer', None, reje_havgående_produkt)
            self.create_produkttype(reje_havgående, 'Reje - havgående licens - Biprodukter', 'Reje - havgående licens - Biprodukter', None, reje_havgående_produkt)

            reje_kystnært_produkt = self.create_produkttype(reje_kystnært, 'Reje - kystnær licens', 'Reje - kystnær licens', None)
            self.create_produkttype(reje_havgående, 'Reje - kystnær licens - Råfrosne skalrejer', 'Reje - kystnær licens - Råfrosne skalrejer', None, reje_kystnært_produkt)
            self.create_produkttype(reje_havgående, 'Reje - kystnær licens - Søkogte skalrejer', 'Reje - kystnær licens - Søkogte skalrejer', None, reje_kystnært_produkt)
            self.create_produkttype(reje_havgående, 'Reje - kystnær licens - Industrirejer-sækkerejer', 'Reje - kystnær licens - Industrirejer-sækkerejer', None, reje_kystnært_produkt)
            self.create_produkttype(reje_havgående, 'Reje - kystnær licens - Biprodukter', 'Reje - kystnær licens - Biprodukter', None, reje_kystnært_produkt)

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
                # ('Torsk', 3, None, 5, None),
                # ('Kuller', 3, None, 5, None),
                # ('Sej', 3, None, 5, None),
                # ('Rødfisk', 3, None, 5, None),
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
