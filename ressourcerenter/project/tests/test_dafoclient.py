
from django.test import TestCase, override_settings
from project.dafo import DatafordelerClient


@override_settings(OPENID={'mock': 'cvr'})
class TestDafoConnection(TestCase):

    # sudo apt install curl
    # curl -k --key /etc/ssl/pitu/key.pem --cert /etc/ssl/pitu/certificate.crt --header "Uxp-client: PITU/GOV/DIA/magenta_services" --header "Uxp-service: PITU/GOV/DIA/magenta_services/DAFO-PRISME-CVR/v1" "https://10.240.76.91/restapi/12950160"
    def test_lookup_company_name(self):
        pass
        """
        Call the dafo-client to get a companyname
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_company_information('1234')
        self.assertEqual('test company_name', result.get('name'))

    def test_lookup_company_other(self):
        """
        Call the dafo-client to get other
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_company_information('1234')
        self.assertEqual('test company_name', result.get('name'))
