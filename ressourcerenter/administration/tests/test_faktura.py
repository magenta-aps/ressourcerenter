from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from administration.models import Afgiftsperiode, FiskeArt, ProduktType, BeregningsModel2021, SkemaType, Faktura
from decimal import Decimal
from datetime import date

from administration.management.commands.create_initial_dataset import Command as CreateInitialDatasetCommand
from administration.management.commands.get_account_data import Command as GetAccountDataCommand
from administration.prisme import Prisme, PrismeSELAccountResponse
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje
from unittest.mock import patch


def prisme_sel_mock(fakturanummer, bogføringsdato):
    xml = f"""
    <CustTable>
        <TotalClaim>-300.00</TotalClaim>
        <TotalPayment>-62.00</TotalPayment>
        <TotalSum>-362.00</TotalSum>
        <TotalRestance>-362.00</TotalRestance>
        <CustTrans>
            <AccountNum>00064305</AccountNum>
            <TransDate>2021-07-01</TransDate>
            <AccountingDate>{bogføringsdato.isoformat()}</AccountingDate>
            <CustGroup>201021</CustGroup>
            <CustGroupName>AMA 2021</CustGroupName>
            <Voucher>RNT-00058035</Voucher>
            <Txt>Testing</Txt>
            <CustPaymCode></CustPaymCode>
            <CustPaymDescription></CustPaymDescription>
            <AmountCur>0.19</AmountCur>
            <RemainAmountCur>0.19</RemainAmountCur>
            <DueDate>2021-07-01</DueDate>
            <Closed></Closed>
            <LastSettleVoucher></LastSettleVoucher>
            <CollectionLetterDate></CollectionLetterDate>
            <CollectionLetterCode>Ingen</CollectionLetterCode>
            <Invoice>123</Invoice>
            <TransType>Renter</TransType>
            <ClaimTypeCode></ClaimTypeCode>
            <RateNmb></RateNmb>
            <ExternalInvoiceNumber>{fakturanummer}</ExternalInvoiceNumber>
        </CustTrans>
    </CustTable>
    """
    return PrismeSELAccountResponse(None, xml)


class FakturaTestCase(TransactionTestCase):

    def setUp(self):
        super().setUpClass()

        CreateInitialDatasetCommand().handle()

        self.beregningsmodel = BeregningsModel2021.objects.create(navn="Testmodel")
        self.periode = Afgiftsperiode.objects.get(dato_fra=date(2021, 1, 1))
        self.periode.beregningsmodel = self.beregningsmodel
        self.periode.save()
        self.skematyper = {s.id: s for s in SkemaType.objects.all()}
        self.virksomhed = Virksomhed.objects.create(cvr=1234)
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

    @patch.object(Prisme, 'get_account_data')
    def test_kontoudtog(self, get_account_data_mock):
        faktura1 = Faktura.objects.create(virksomhed=self.virksomhed, beløb=Decimal(200), betalingsdato=date(2022, 7, 1), kode=123, opretter=self.user)
        dato = date(2021, 5, 1)
        get_account_data_mock.return_value = [prisme_sel_mock(faktura1.id, dato)]
        GetAccountDataCommand().handle()
        faktura1.refresh_from_db()
        self.assertEquals(faktura1.bogført, dato)

    def test_text(self):
        periode = Afgiftsperiode(navn_dk='x'*200, dato_fra=date(2000, 1, 1), dato_til=date(2000, 3, 31))
        indberetning = Indberetning(afgiftsperiode=periode, skematype=self.skematyper[1], virksomhed=self.virksomhed)
        linje = IndberetningLinje(indberetning=indberetning, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        faktura = Faktura(virksomhed=self.virksomhed, beløb=Decimal(200), betalingsdato=date(2022, 7, 1), kode=123, opretter=self.user, periode=periode, linje=linje)
        for line in faktura.text.splitlines():
            self.assertFalse(len(line) > 60)
