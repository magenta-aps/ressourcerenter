from administration.models import (
    Afgiftsperiode,
    SatsTabelElement,
    ProduktType,
    BeregningsModel2021,
    FiskeArt,
    SkemaType,
)
from datetime import date
from decimal import Decimal
from django.test import TestCase
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje
from uuid import uuid4


class AfgiftTestCase(TestCase):
    """
    §4
    Test at havgående fiskeri efter
        rejer, hellefisk, torsk, krabber, kuller, sej, rødfisk og kammuslinger
    Test at kystnært fiskeri efter
        rejer og hellefisk
    beskattes iht. §§4-7
    """

    def setUp(self):
        super().setUp()
        self.periode = Afgiftsperiode.objects.create(
            dato_fra=date(2021, 1, 1), dato_til=date(2021, 3, 31)
        )

        beregningsmodel = BeregningsModel2021.objects.create(
            navn="TestBeregningsModel",
        )

        self.periode.beregningsmodel = beregningsmodel
        self.periode.save()

        for navn, skematype_id, fartoej_groenlandsk, rate_procent, rate_pr_kg in [
            ("Reje - havgående licens", 1, None, 5, None),
            ("Reje - kystnær licens", 1, None, 5, None),
            ("Hellefisk", 1, None, 5, None),
            ("Torsk", 1, None, 5, None),
            ("Kuller", 1, None, 5, None),
            ("Sej", 1, None, 5, None),
            ("Rødfisk", 1, None, 5, None),
            ("Sild", 1, True, None, 0.25),
            ("Sild", 1, False, None, 0.8),
            ("Lodde", 1, True, None, 0.15),
            ("Lodde", 1, False, None, 0.7),
            ("Makrel", 1, True, None, 0.4),
            ("Makrel", 1, False, None, 1),
            ("Blåhvilling", 1, True, None, 0.15),
            ("Blåhvilling", 1, False, None, 0.7),
            ("Guldlaks", 1, True, None, 0.15),
            ("Guldlaks", 1, False, None, 0.7),
        ]:
            fiskeart = FiskeArt.objects.get(navn_dk=navn)
            skematype = SkemaType.objects.get(id=skematype_id)
            fiskeart.skematype.set([skematype])
            sats = SatsTabelElement.objects.get(
                periode=self.periode,
                skematype=skematype,
                fiskeart=fiskeart,
                fartoej_groenlandsk=fartoej_groenlandsk,
            )

            sats.rate_procent = rate_procent
            sats.rate_pr_kg = rate_pr_kg
            sats.save()

        self.virksomhed, _ = Virksomhed.objects.get_or_create(cvr=1234)

    def _calculate(
        self,
        skematype_id=1,
        fiskeart=None,
        salgspris=0,
        levende_vaegt=0,
        salgsvaegt=0,
        fartoej_groenlandsk=None,
    ):
        indberetning = Indberetning.objects.create(
            afgiftsperiode=self.periode,
            virksomhed=self.virksomhed,
            skematype=SkemaType.objects.get(id=skematype_id),
        )
        IndberetningLinje.objects.create(
            indberetning=indberetning,
            produkttype=ProduktType.objects.filter(
                fiskeart__navn_dk=fiskeart, fartoej_groenlandsk=fartoej_groenlandsk
            ).first(),
            salgspris=Decimal(salgspris),
            levende_vægt=Decimal(levende_vaegt),
            produktvægt=Decimal(salgsvaegt),
        )
        model = BeregningsModel2021.objects.create(navn=uuid4())
        result = model.calculate(indberetning)
        return result[0]

    def test_transferred_calculation_1(self):
        """
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) < 12 kr/kg
        er grundafgift 0.20 kr.pr.kg
        """
        rate_element = SatsTabelElement.objects.get(
            periode=self.periode,
            skematype__id=1,
            fiskeart__navn_dk="Reje - havgående licens",
        )
        rate_element.rate_procent = Decimal(0)
        rate_element.rate_pr_kg = Decimal(0.2)
        rate_element.save()

        result = self._calculate(
            fiskeart="Reje - havgående licens",
            skematype_id=1,
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
        )
        self.assertEquals(result.afgift, Decimal(20))

    def test_landed_calculation_2(self):
        """
        §5.2
        Hvis der er indhandlet i Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) < 8 kr.pr.kg
        er grundafgift 0.05 kr.pr.kg
        """
        rate_element = SatsTabelElement.objects.get(
            periode=self.periode,
            skematype__id=1,
            fiskeart__navn_dk="Reje - havgående licens",
        )
        rate_element.rate_procent = None
        rate_element.rate_pr_kg = Decimal(0.05)
        rate_element.save()

        result = self._calculate(
            fiskeart="Reje - havgående licens",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
        )

        self.assertEquals(result.afgift, Decimal(5))

    def test_transferred_calculation_2(self):
        """
        §6
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) >= 12 kr/kg og < 17 kr/kg
        er ressourcerenteafgift 5% af prisen
        §7
        Ved indhandling
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) >= 8 kr/kg
        er ressourcerenteafgift 5% af prisen
        """
        result = self._calculate(
            fiskeart="Reje - havgående licens",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
        )
        self.assertEquals(Decimal(50), result.afgift)

        result = self._calculate(
            fiskeart="Torsk", salgspris=500, levende_vaegt=100, salgsvaegt=100
        )
        self.assertEquals(Decimal(25), result.afgift)

        result = self._calculate(
            fiskeart="Hellefisk", salgspris=300, levende_vaegt=150, salgsvaegt=150
        )
        self.assertEquals(Decimal(15), result.afgift)

    def test_transferred_calculation_3(self):
        """
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) >= 17 kr/kg
        er ressourcerenteafgift 5% + 1% pr kr i gnsn salgspris (rundet op, så 17,5 kr/kg = 6%, 18,5 kr/kg = 7%)
        Dog max 17,5%
        """
        rate_element = SatsTabelElement.objects.get(
            periode=self.periode,
            skematype__id=1,
            fiskeart__navn_dk="Reje - havgående licens",
        )
        rate_element.rate_pr_kg = None
        rate_element.rate_procent = Decimal(7)
        rate_element.save()

        result = self._calculate(
            fiskeart="Reje - havgående licens",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
        )

        self.assertEquals(result.afgift, Decimal(70))

    def test_pelagic(self):
        """
        §8
        Pelagisk fiskeri - afgifter for fartøj fra
                Grønland | Andre
        Sild        0,25 | 0,80
        Lodde       0,15 | 0,70
        Makrel      0,40 | 1,00
        Blåhvilling 0,15 | 0,70
        Guldlaks    0,15 | 0,70
        kr.pr.kg levende vægt
        """
        result = self._calculate(
            fiskeart="Sild",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=True,
        )
        self.assertEquals(result.afgift, Decimal(25))

        result = self._calculate(
            fiskeart="Sild",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=False,
        )
        self.assertEquals(result.afgift, Decimal(80))

        result = self._calculate(
            fiskeart="Lodde",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=True,
        )
        self.assertEquals(result.afgift, Decimal(15))

        result = self._calculate(
            fiskeart="Lodde",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=False,
        )
        self.assertEquals(result.afgift, Decimal(70))

        result = self._calculate(
            fiskeart="Makrel",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=True,
        )
        self.assertEquals(result.afgift, Decimal(40))

        result = self._calculate(
            fiskeart="Makrel",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=False,
        )
        self.assertEquals(result.afgift, Decimal(100))

        result = self._calculate(
            fiskeart="Blåhvilling",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=True,
        )
        self.assertEquals(result.afgift, Decimal(15))

        result = self._calculate(
            fiskeart="Blåhvilling",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=False,
        )
        self.assertEquals(result.afgift, Decimal(70))

        result = self._calculate(
            fiskeart="Guldlaks",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=True,
        )
        self.assertEquals(result.afgift, Decimal(15))

        result = self._calculate(
            fiskeart="Guldlaks",
            salgspris=1000,
            levende_vaegt=100,
            salgsvaegt=100,
            fartoej_groenlandsk=False,
        )
        self.assertEquals(result.afgift, Decimal(70))
