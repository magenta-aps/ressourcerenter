
from django.test import TestCase, override_settings
from project.dafo import DatafordelerClient


class TestDafoConnection(TestCase):

    # sudo apt install curl
    # curl -k --key /etc/ssl/pitu/key.pem --cert /etc/ssl/pitu/certificate.crt --header "Uxp-client: PITU/GOV/DIA/magenta_services" --header "Uxp-service: PITU/GOV/DIA/magenta_services/DAFO-PRISME-CVR/v1" "https://10.240.76.91/restapi/12950160"
    def test_lookup_company_name(self):
        """
        Call the dafo-client to get a companyinfo
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_address_and_name('12950160', 'cvr')
        self.assertEqual({'name': 'navn', 'address': 'adresse\n0000 ', 'country': 'GL'}, result)

    def test_lookup_company_other(self):
        """
        Call the dafo-client to get a personinfo
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_address_and_name('1111111111', 'cpr')
        self.assertEqual({'name': 'fornavn efternavn', 'address': 'adresse\n0000 ', 'country': 'GL'}, result)
