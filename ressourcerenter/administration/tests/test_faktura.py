from datetime import date, datetime
from decimal import Decimal

from administration.models import (
    Afgiftsperiode,
    BeregningsModel2021,
    Faktura,
    FiskeArt,
    ProduktType,
    SatsTabelElement,
    SkemaType,
)
from django.contrib.auth import get_user_model
from django.test import TestCase
from indberetning.models import (
    Indberetning,
    IndberetningLinje,
    Indhandlingssted,
    Virksomhed,
)
from tenQ.writer import G69TransactionWriter


class FakturaTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create(username="TestUser")
        self.skematype, _ = SkemaType.objects.get_or_create(
            id=1, defaults={"navn_dk": "Havgående"}
        )
        self.fiskeart, _ = FiskeArt.objects.get_or_create(navn_dk="Makrel")
        self.fiskeart.skematype.set([self.skematype])
        self.produkttype, _ = ProduktType.objects.get_or_create(
            fiskeart=self.fiskeart, fartoej_groenlandsk=False
        )
        self.sted = Indhandlingssted.objects.get(navn="Nuuk")

    def test_text_split(self):
        virksomhed = Virksomhed.objects.create(cvr=1234, sted=self.sted)
        periode = Afgiftsperiode(
            navn_dk="x" * 200, dato_fra=date(2022, 1, 1), dato_til=date(2022, 3, 31)
        )
        indberetning = Indberetning(
            afgiftsperiode=periode, skematype=self.skematype, virksomhed=virksomhed
        )
        linje = IndberetningLinje(
            indberetning=indberetning,
            produkttype=ProduktType.objects.get(
                fiskeart__navn_dk="Makrel", fartoej_groenlandsk=False
            ),
            levende_vægt=1000,
            salgspris=10000,
        )
        faktura = Faktura(
            virksomhed=virksomhed,
            beløb=Decimal(200),
            betalingsdato=date(2022, 7, 1),
            opkrævningsdato=date(2022, 7, 1),
            kode=123,
            opretter=self.user,
            periode=periode,
            linje=linje,
        )
        for line in faktura.text.splitlines():
            self.assertFalse(len(line) > 60)

    def test_g69(self):
        virksomhed = Virksomhed.objects.create(cvr="12345678", sted=self.sted)
        betalingsdato = date(2022, 1, 1)
        beregningsmodel = BeregningsModel2021.objects.create(
            navn="FakturaTestBeregningsModel"
        )
        periode = Afgiftsperiode.objects.create(
            beregningsmodel=beregningsmodel,
            navn_dk="testperiode",
            dato_fra=date(2022, 1, 1),
            dato_til=date(2022, 3, 31),
        )
        sats = SatsTabelElement.objects.get(
            periode=periode,
            skematype=self.skematype,
            fiskeart=self.fiskeart,
            fartoej_groenlandsk=False,
        )
        sats.rate_procent = None
        sats.rate_pr_kg = 1
        sats.save()
        indberetning = Indberetning.objects.create(
            afgiftsperiode=periode, skematype=self.skematype, virksomhed=virksomhed
        )
        linje = IndberetningLinje.objects.create(
            indberetning=indberetning,
            produkttype=ProduktType.objects.get(
                fiskeart__navn_dk="Makrel", fartoej_groenlandsk=False
            ),
            levende_vægt=1000,
            salgspris=10000,
        )
        linje.indberetningstidspunkt = datetime(2022, 3, 21, 12, 0, 0)
        linje.calculate_afgift()
        writer = G69TransactionWriter(registreringssted=0, organisationsenhed=0)
        faktura = Faktura.objects.create(
            virksomhed=virksomhed,
            beløb=linje.afgift,
            betalingsdato=betalingsdato,
            kode=123,
            opretter=self.user,
            periode=periode,
            opkrævningsdato=Faktura.get_opkrævningsdato(
                linje.indberetningstidspunkt.date()
            ),
        )
        linje.faktura = faktura
        linje.save(update_fields=("faktura",))

        self.assertEqual(
            faktura.prismeG69_content(writer),
            "000G6900001000001NORFLYD&10300000&1040000001&11020220321&111241126242040197&112000000100000 &113D&13203&13312345678&153Makrel, 1.kv 2022&2501\r\n"
            "000G6900002000001NORFLYD&10300000&1040000001&11020220321&111220104600110022&112000000100000-&113K&13203&13312345678&153Makrel, 1.kv 2022&2501",
        )
