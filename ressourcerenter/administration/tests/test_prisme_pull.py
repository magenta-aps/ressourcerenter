from administration.models import Faktura
from administration.prisme import Prisme, PrismeSELAccountResponse
from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core import management
from django.test import TestCase
from indberetning.models import Virksomhed
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


class PrismeTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.virksomhed = Virksomhed.objects.create(cvr=1234)
        self.user = get_user_model().objects.create(username="TestUser")

    @patch.object(Prisme, "get_account_data")
    def test_kontoudtog(self, get_account_data_mock):
        faktura = Faktura.objects.create(
            virksomhed=self.virksomhed,
            beløb=Decimal(200),
            betalingsdato=date(2022, 7, 1),
            opkrævningsdato=date(2022, 7, 1),
            kode=123,
            opretter=self.user,
        )
        dato = date(2021, 5, 1)
        get_account_data_mock.return_value = [prisme_sel_mock(faktura.id, dato)]
        management.call_command("get_account_data")
        faktura.refresh_from_db()
        self.assertEquals(faktura.bogført, dato)
