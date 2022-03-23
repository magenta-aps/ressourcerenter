from administration.models import Afgiftsperiode, FiskeArt, ProduktType, SkemaType, Faktura
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core import management
from django.test import TransactionTestCase
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje


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
        periode = Afgiftsperiode(navn_dk='x'*200, dato_fra=date(2000, 1, 1), dato_til=date(2000, 3, 31))
        indberetning = Indberetning(afgiftsperiode=periode, skematype=self.skematyper[1], virksomhed=virksomhed)
        linje = IndberetningLinje(indberetning=indberetning, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        faktura = Faktura(virksomhed=virksomhed, beløb=Decimal(200), betalingsdato=date(2022, 7, 1), kode=123, opretter=self.user, periode=periode, linje=linje)
        for line in faktura.text.splitlines():
            self.assertFalse(len(line) > 60)
