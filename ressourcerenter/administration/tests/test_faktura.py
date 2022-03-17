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

    def test_create_fakturaer(self):
        betalingsdato = date(2022, 1, 1)
        # Opret et antal indberetningslinjer på forskellige produkttyper, og tjek at de rigtige fakturaer genereres
        indberetning1 = Indberetning.objects.create(afgiftsperiode=self.periode, skematype=self.skematyper[1], virksomhed=self.virksomhed)
        indberetning2 = Indberetning.objects.create(afgiftsperiode=self.periode, skematype=self.skematyper[2], virksomhed=self.virksomhed)

        linje1a = IndberetningLinje.objects.create(indberetning=indberetning1, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        faktura1a = self.faktura_from_linje(linje1a, self.user, betalingsdato)
        self.assertEquals(faktura1a.beløb, Decimal(1000))
        self.assertEquals(faktura1a.virksomhed, self.virksomhed)

        linje1b = IndberetningLinje.objects.create(indberetning=indberetning1, produkttype=ProduktType.objects.get(navn_dk='Torsk - Hel fisk'), levende_vægt=2000, salgspris=20000)
        faktura1b = self.faktura_from_linje(linje1b, self.user, betalingsdato)
        self.assertEquals(faktura1b.beløb, Decimal(1000))

        linje1c = IndberetningLinje.objects.create(indberetning=indberetning1, produkttype=ProduktType.objects.get(navn_dk='Torsk - Filet'), levende_vægt=3000, salgspris=30000)
        faktura1c = self.faktura_from_linje(linje1c, self.user, betalingsdato)
        self.assertEquals(faktura1c.beløb, Decimal(1500))

        linje1d = IndberetningLinje.objects.create(indberetning=indberetning1, produkttype=ProduktType.objects.get(navn_dk='Reje - havgående licens - Råfrosne skalrejer'), levende_vægt=4000, salgspris=40000)
        faktura1d = self.faktura_from_linje(linje1d, self.user, betalingsdato)
        self.assertEquals(faktura1d.beløb, Decimal(2000))

        linje2a = IndberetningLinje.objects.create(indberetning=indberetning2, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        faktura2a = self.faktura_from_linje(linje2a, self.user, betalingsdato)
        self.assertEquals(faktura2a.beløb, Decimal(1000))

        linje2b = IndberetningLinje.objects.create(indberetning=indberetning2, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=500, salgspris=5000)
        faktura2b = self.faktura_from_linje(linje2b, self.user, betalingsdato)
        self.assertEquals(faktura2b.beløb, Decimal(500))

        linje2c = IndberetningLinje.objects.create(indberetning=indberetning2, produkttype=ProduktType.objects.get(navn_dk='Torsk - Hel fisk'), levende_vægt=2000, salgspris=20000)
        faktura2c = self.faktura_from_linje(linje2c, self.user, betalingsdato)
        self.assertEquals(faktura2c.beløb, Decimal(1000))

        linje2d = IndberetningLinje.objects.create(indberetning=indberetning2, produkttype=ProduktType.objects.get(navn_dk='Torsk - Filet'), levende_vægt=3000, salgspris=30000)
        faktura2d = self.faktura_from_linje(linje2d, self.user, betalingsdato)
        self.assertEquals(faktura2d.beløb, Decimal(1500))

        linje2e = IndberetningLinje.objects.create(indberetning=indberetning2, produkttype=ProduktType.objects.get(navn_dk='Reje - kystnær licens - Industrirejer-sækkerejer'), levende_vægt=4000, salgspris=40000)
        faktura2e = self.faktura_from_linje(linje2e, self.user, betalingsdato)
        self.assertEquals(faktura2e.beløb, Decimal(2000))

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

    @staticmethod
    def faktura_from_linje(linje, opretter, betalingsdato, batch=None):
        return Faktura(
            kode=linje.debitorgruppekode,
            periode=linje.indberetning.afgiftsperiode,
            opretter=opretter,
            virksomhed=linje.indberetning.virksomhed,
            betalingsdato=betalingsdato,
            batch=batch,
            beløb=linje.afgift
        )

    """
        Udeladt for nu; sender fil til prismes testsystem, så det skal vi ikke spamme dem med.
        Kan testes lokalt ved at sætte følgende i docker-compose.override.yml:
          - TENQ_HOST=172.17.0.1
          - TENQ_PORT=2222
          - TENQ_USER=<brugernavn fra bitwarden (Grønland/Skattestyrelsen/KAS Prisme 10Q password)>
          - TENQ_PASSWORD=<password fra bitwarden>
        ... samt åbne en tunnel med:
            ssh -L 172.17.0.1:2222:sftp.erp.gl:22 larsp@10.240.76.76

    def test_upload(self):
        indberetning1 = Indberetning.objects.create(afgiftsperiode=self.periode, skematype=self.skematyper[1], virksomhed=self.virksomhed)
        linje1 = IndberetningLinje.objects.create(indberetning=indberetning1, produkttype=ProduktType.objects.get(navn_dk='Makrel, ikke-grønlandsk fartøj'), levende_vægt=1000, salgspris=10000)
        betalingsdato = date.today() + timedelta(days=7)
        batch = Prisme10QBatch.objects.create(oprettet_af=self.user)
        fakturaer = Faktura.opret_fakturaer([linje1], self.user, betalingsdato, batch)
        batch.send('10q_development', self.user)
        self.assertEquals(batch.status, Prisme10QBatch.STATUS_CREATED)
    """
