from administration.models import SkemaType, FiskeArt, ProduktType, Afgiftsperiode, SatsTabelElement
from django.core.management.base import BaseCommand
from django.utils import timezone
from indberetning.models import Indhandlingssted
from administration.models import G69Code
from project.dateutil import quarter_first_date, quarter_last_date


class Command(BaseCommand):
    help = 'Create basic data'

    def handle(self, *args, **options):
        self.create_skematyper()
        self.create_fiskearter()
        self.create_produkttyper()
        self.create_afgiftsperioder()
        self.create_indhandlingssteder()
        self.create_g69_koder()

    def create_fiskeart(self, navn_dk, navn_gl, pelagisk, skematype_ids):
        fiskeart, _ = FiskeArt.objects.update_or_create(
            navn_dk=navn_dk,
            defaults={
                'navn_gl': navn_gl,
                'pelagisk': pelagisk,
            }
        )
        fiskeart.skematype.set([self.skematyper[id] for id in skematype_ids])
        fiskeart.save()
        return fiskeart

    def create_produkttype(self, fiskeart, navn_dk, navn_gl, fartoej_groenlandsk=None, gruppe=None, aktivitetskode_alle=None, **kwargs):
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

    def create_produkttype_subtype(self, parent, navn_dk, navn_gl):
        self.create_produkttype(
            parent.fiskeart,
            ' - '.join([parent.navn_dk, navn_dk]),
            ' - '.join([parent.navn_gl, navn_gl]),
            gruppe=parent,
        )

    def create_skematyper(self):
        self.skematyper = {}
        if not SkemaType.objects.exists():
            for id, navn in [
                (1, "Havgående fartøjer og kystnære rejefartøjer - producerende fartøjer"),
                (2, "Indhandlinger - Indberetninger fra fabrikkerne / Havgående fiskeri og kystnært fiskeri efter rejer"),
                (3, "Kystnært fiskeri efter andre arter end rejer - indberetninger fra fabrikkerne"),
            ]:
                self.skematyper[id], _ = SkemaType.objects.get_or_create(id=id, navn_dk=navn, navn_gl=navn)

    def create_fiskearter(self):
        if not FiskeArt.objects.exists():
            self.create_fiskeart('Makrel', 'Makrel', True, [1, 2])
            self.create_fiskeart('Sild', 'Sild', True, [1, 2])
            self.create_fiskeart('Lodde', 'Lodde', True, [1, 2])
            self.create_fiskeart('Blåhvilling', 'Blåhvilling', True, [1, 2])
            self.create_fiskeart('Guldlaks', 'Guldlaks', True, [1, 2])
            self.create_fiskeart('Hellefisk', 'Hellefisk', False, [1, 2, 3])
            self.create_fiskeart('Torsk', 'Torsk', False, [1, 2])
            self.create_fiskeart('Kuller', 'Kuller', False, [1, 2])
            self.create_fiskeart('Sej', 'Sej', False, [1, 2])
            self.create_fiskeart('Rødfisk', 'Rødfisk', False, [1, 2])
            self.create_fiskeart('Reje - havgående licens', 'Reje - havgående licens', False, [1, 2])
            self.create_fiskeart('Reje - kystnær licens', 'Reje - kystnær licens', False, [1, 2])
            self.create_fiskeart('Reje - Svalbard og Barentshavet', 'Reje - Svalbard og Barentshavet', False, [1, 2])

    def create_produkttyper(self):
        makrel = FiskeArt.objects.get(navn_dk='Makrel')
        self.create_produkttype(
            makrel,
            f"{makrel.navn_dk}, grønlandsk fartøj", f"{makrel.navn_gl}, grønlandsk fartøj",
            fartoej_groenlandsk=True,
            aktivitetskode_alle=10021,
        )
        self.create_produkttype(
            makrel,
            f"{makrel.navn_dk}, ikke-grønlandsk fartøj", f"{makrel.navn_gl}, ikke-grønlandsk fartøj",
            fartoej_groenlandsk=False,
            aktivitetskode_alle=10022,
        )

        sild = FiskeArt.objects.get(navn_dk='Sild')
        self.create_produkttype(
            sild,
            f"{sild.navn_dk}, grønlandsk fartøj", f"{sild.navn_gl}, grønlandsk fartøj",
            fartoej_groenlandsk=True,
            aktivitetskode_alle=10023,
        )
        self.create_produkttype(
            sild,
            f"{sild.navn_dk}, ikke-grønlandsk fartøj", f"{sild.navn_gl}, ikke-grønlandsk fartøj",
            fartoej_groenlandsk=False,
            aktivitetskode_alle=10024
        )

        lodde = FiskeArt.objects.get(navn_dk='Lodde')
        self.create_produkttype(
            lodde,
            f"{lodde.navn_dk}, grønlandsk fartøj", f"{lodde.navn_gl}, grønlandsk fartøj",
            fartoej_groenlandsk=True,
            aktivitetskode_alle=10025
        )
        self.create_produkttype(
            lodde,
            f"{lodde.navn_dk}, ikke-grønlandsk fartøj", f"{lodde.navn_gl}, ikke-grønlandsk fartøj",
            fartoej_groenlandsk=False,
            aktivitetskode_alle=10026
        )

        blåhvilling = FiskeArt.objects.get(navn_dk='Blåhvilling')
        self.create_produkttype(
            blåhvilling,
            f"{blåhvilling.navn_dk}, grønlandsk fartøj", f"{blåhvilling.navn_gl}, grønlandsk fartøj",
            fartoej_groenlandsk=True,
            aktivitetskode_alle=10038
        )
        self.create_produkttype(
            blåhvilling,
            f"{blåhvilling.navn_dk}, ikke-grønlandsk fartøj", f"{blåhvilling.navn_gl}, ikke-grønlandsk fartøj",
            fartoej_groenlandsk=False,
            aktivitetskode_alle=10039
        )

        guldlaks = FiskeArt.objects.get(navn_dk='Guldlaks')
        self.create_produkttype(
            guldlaks,
            f"{guldlaks.navn_dk}, grønlandsk fartøj", f"{guldlaks.navn_gl}, grønlandsk fartøj",
            fartoej_groenlandsk=True,
            aktivitetskode_alle=10040
        )
        self.create_produkttype(
            guldlaks,
            f"{guldlaks.navn_dk}, ikke-grønlandsk fartøj", f"{guldlaks.navn_gl}, ikke-grønlandsk fartøj",
            fartoej_groenlandsk=False,
            aktivitetskode_alle=10041
        )

        hellefisk = FiskeArt.objects.get(navn_dk='Hellefisk')
        hellefisk_produkt = self.create_produkttype(
            hellefisk,
            hellefisk.navn_dk, hellefisk.navn_gl,
            aktivitetskode_havgående=10011,
            aktivitetskode_kystnært=10012,
            aktivitetskode_indhandling=10013,
        )
        self.create_produkttype_subtype(hellefisk_produkt, 'Hel fisk', 'Hel fisk')
        self.create_produkttype_subtype(hellefisk_produkt, 'Filet', 'Filet')
        self.create_produkttype_subtype(hellefisk_produkt, 'Biprodukter', 'Biprodukter')

        torsk = FiskeArt.objects.get(navn_dk='Torsk')
        torsk_produkt = self.create_produkttype(
            torsk,
            torsk.navn_dk, torsk.navn_gl,
            aktivitetskode_havgående=10027,
            aktivitetskode_indhandling=10028,
        )
        self.create_produkttype_subtype(torsk_produkt, 'Hel fisk', 'Hel fisk')
        self.create_produkttype_subtype(torsk_produkt, 'Filet', 'Filet')
        self.create_produkttype_subtype(torsk_produkt, 'Biprodukter', 'Biprodukter')

        kuller = FiskeArt.objects.get(navn_dk='Kuller')
        kuller_produkt = self.create_produkttype(
            kuller,
            kuller.navn_dk, kuller.navn_gl,
            aktivitetskode_havgående=10031,
            aktivitetskode_indhandling=10032
        )
        self.create_produkttype_subtype(kuller_produkt, 'Hel fisk', 'Hel fisk')
        self.create_produkttype_subtype(kuller_produkt, 'Filet', 'Filet')
        self.create_produkttype_subtype(kuller_produkt, 'Biprodukter', 'Biprodukter')

        sej = FiskeArt.objects.get(navn_dk='Sej')
        sej_produkt = self.create_produkttype(
            sej,
            sej.navn_dk, sej.navn_gl,
            aktivitetskode_havgående=10033,
            aktivitetskode_indhandling=10034
        )
        self.create_produkttype_subtype(sej_produkt, 'Hel fisk', 'Hel fisk')
        self.create_produkttype_subtype(sej_produkt, 'Filet', 'Filet')
        self.create_produkttype_subtype(sej_produkt, 'Biprodukter', 'Biprodukter')

        rødfisk = FiskeArt.objects.get(navn_dk='Rødfisk')
        rødfisk_produkt = self.create_produkttype(
            rødfisk,
            rødfisk.navn_dk, rødfisk.navn_gl,
            aktivitetskode_havgående=10029,
            aktivitetskode_indhandling=10030,
        )
        self.create_produkttype_subtype(rødfisk_produkt, 'Hel fisk', 'Hel fisk')
        self.create_produkttype_subtype(rødfisk_produkt, 'Filet', 'Filet')
        self.create_produkttype_subtype(rødfisk_produkt, 'Biprodukter', 'Biprodukter')

        reje_havgående = FiskeArt.objects.get(navn_dk='Reje - havgående licens')
        reje_havgående_produkt = self.create_produkttype(
            reje_havgående,
            reje_havgående.navn_dk, reje_havgående.navn_gl,
            aktivitetskode_havgående=10011,
            fangsttype='havgående',
        )
        self.create_produkttype_subtype(reje_havgående_produkt, 'Råfrosne skalrejer', 'Råfrosne skalrejer')
        self.create_produkttype_subtype(reje_havgående_produkt, 'Søkogte skalrejer', 'Søkogte skalrejer')
        self.create_produkttype_subtype(reje_havgående_produkt, 'Industrirejer-sækkerejer', 'Industrirejer-sækkerejer')
        self.create_produkttype_subtype(reje_havgående_produkt, 'Biprodukter', 'Biprodukter')

        reje_kystnært = FiskeArt.objects.get(navn_dk='Reje - kystnær licens')
        reje_kystnært_produkt = self.create_produkttype(
            reje_kystnært,
            reje_kystnært.navn_dk, reje_kystnært.navn_gl,
            aktivitetskode_kystnært=10012,
            fangsttype='kystnært',
        )
        self.create_produkttype_subtype(reje_kystnært_produkt, 'Råfrosne skalrejer', 'Råfrosne skalrejer')
        self.create_produkttype_subtype(reje_kystnært_produkt, 'Søkogte skalrejer', 'Søkogte skalrejer')
        self.create_produkttype_subtype(reje_kystnært_produkt, 'Industrirejer-sækkerejer', 'Industrirejer-sækkerejer')
        self.create_produkttype_subtype(reje_kystnært_produkt, 'Biprodukter', 'Biprodukter')

        reje_svalbard = FiskeArt.objects.get(navn_dk='Reje - Svalbard og Barentshavet')
        reje_svalbard_produkt = self.create_produkttype(
            reje_svalbard,
            reje_svalbard.navn_dk, reje_svalbard.navn_gl,
            aktivitetskode_svalbard=10014,
            fangsttype='svalbard',
        )
        self.create_produkttype_subtype(reje_svalbard_produkt, 'Råfrosne skalrejer', 'Råfrosne skalrejer')
        self.create_produkttype_subtype(reje_svalbard_produkt, 'Søkogte skalrejer', 'Søkogte skalrejer')
        self.create_produkttype_subtype(reje_svalbard_produkt, 'Industrirejer-sækkerejer', 'Industrirejer-sækkerejer')
        self.create_produkttype_subtype(reje_svalbard_produkt, 'Biprodukter', 'Biprodukter')

    def create_afgiftsperioder(self):
        perioder = []
        if not Afgiftsperiode.objects.exists():
            today = timezone.now().date()
            for year in (2022,):
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

    def create_indhandlingssteder(self):
        for stedkode, navn in (
            (10310, 'Nanortalik'),
            (10312, 'Aappilattoq ved Nanortalik'),
            (10320, 'Qaqortoq'),
            (10330, 'Narsaq'),
            (10331, 'Igaliku Kujalleq'),
            (10450, 'Paamiut'),
            (10451, 'Arsuk'),
            (10460, 'Nuuk'),
            (10461, 'Qeqertarsuatsiaat'),
            (10486, 'Kuummiut / Kuummiit'),
            (10570, 'Maniitsoq'),
            (10571, 'Atammik'),
            (10573, 'Kangaamiut'),
            (10580, 'Sisimiut'),
            (10583, 'Sarfannguaq / Sarfannguit'),
            (10601, 'Aasiaat'),
            (10603, 'Akunnaaq'),
            (10610, 'Qasigiannguit'),
            (10611, 'Ikamiut'),
            (10640, 'Qeqertarsuaq'),
            (10690, 'Kangaatsiaq'),
            (10692, 'Attu'),
            (10700, 'Avannaata Kommunia'),
            (10720, 'Ilulissat'),
            (10721, 'Oqaatsut'),
            (10722, 'Qeqertaq'),
            (10723, 'Saqqaq'),
            (10750, 'Uummannaq'),
            (10752, 'Qaarsut'),
            (10753, 'Ikerasak'),
            (10754, 'Saattut'),
            (10755, 'Ukkusissat'),
            (10760, 'Upernavik'),
            (10763, 'Aappilattoq ved Upernavik'),
            (10765, 'Tasiusaq-Nutaarmiut'),
            (10766, 'Nuussuaq'),
            (10767, 'Kullorsuaq'),
            (10769, 'Innaarsuit'),
            (10770, 'Qaanaaq'),
            (10779, 'Nutaarmiut'),
        ):
            Indhandlingssted.objects.update_or_create(
                stedkode=stedkode,
                defaults={'navn': navn}
            )

    def create_g69_koder(self):
        for år in range(2020, 2025):
            G69Code.generate_for_year(år)
