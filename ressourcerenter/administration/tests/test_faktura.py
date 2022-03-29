from administration.models import Afgiftsperiode, FiskeArt, ProduktType, SkemaType, Faktura
from administration.models import BeregningsModel2021
from datetime import date
from datetime import datetime
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core import management
from django.test import TransactionTestCase
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje
from tenQ.writer import G69TransactionWriter


class FakturaTestCase(TransactionTestCase):

    def setUp(self):
        super().setUpClass()
        management.call_command('create_initial_dataset')
        self.skematyper = {s.id: s for s in SkemaType.objects.all()}
        self.user = get_user_model().objects.create(username="TestUser")

    def test_fiskeart_debitorgruppenummer(self):
        reje = FiskeArt.objects.get(navn_dk='Reje - havgående licens')
        for id in self.skematyper:
            self.assertEquals(reje.get_debitorgruppekode(self.skematyper[id]), 107)
        reje = FiskeArt.objects.get(navn_dk='Reje - kystnær licens')
        for id in self.skematyper:
            self.assertEquals(reje.get_debitorgruppekode(self.skematyper[id]), 307)

        makrel = FiskeArt.objects.get(navn_dk='Makrel')
        self.assertEquals(makrel.get_debitorgruppekode(self.skematyper[1]), 106)
        self.assertEquals(makrel.get_debitorgruppekode(self.skematyper[2]), 206)
        self.assertEquals(makrel.get_debitorgruppekode(self.skematyper[3]), 306)

    def test_text_split(self):
        virksomhed = Virksomhed.objects.create(cvr=1234)
        periode = Afgiftsperiode(navn_dk='x'*200, dato_fra=date(2022, 1, 1), dato_til=date(2022, 3, 31))
        indberetning = Indberetning(afgiftsperiode=periode, skematype=self.skematyper[1], virksomhed=virksomhed)
        linje = IndberetningLinje(indberetning=indberetning, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        faktura = Faktura(
            virksomhed=virksomhed, beløb=Decimal(200), betalingsdato=date(2022, 7, 1), opkrævningsdato=date(2022, 7, 1),
            kode=123, opretter=self.user, periode=periode, linje=linje
        )
        for line in faktura.text.splitlines():
            self.assertFalse(len(line) > 60)

    def test_g69(self):
        virksomhed = Virksomhed.objects.create(cvr=1234)
        betalingsdato = date(2022, 1, 1)
        beregningsmodel = BeregningsModel2021.objects.create(navn='TestBeregningsModel')
        periode = Afgiftsperiode.objects.first()
        periode.beregningsmodel = beregningsmodel
        indberetning = Indberetning.objects.create(
            afgiftsperiode=periode,
            skematype=self.skematyper[1],
            virksomhed=virksomhed
        )
        linje = IndberetningLinje.objects.create(
            indberetning=indberetning,
            produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'),
            levende_vægt=1000,
            salgspris=10000
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
            periode=periode, linje=linje,
            opkrævningsdato=Faktura.get_opkrævningsdato(linje.indberetningstidspunkt.date())
        )
        self.assertEquals(
            faktura.prismeG69_content(writer),
            "000G6900001000001NORFLYD&10300000&1040000001&11020220321&1110000000000&112000000100000 &113D&13203&1330000001234&153Afgift for Makrel, 1. kvartal&2501\r\n"
            "000G6900002000001NORFLYD&10300000&1040000001&11020220321&1110000000000&112000000100000 &113K&13203&1330000001234&153Afgift for Makrel, 1. kvartal&2501"
        )
