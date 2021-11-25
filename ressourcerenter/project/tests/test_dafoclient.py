
from django.test import TestCase, override_settings
from project.dafo import DatafordelerClient


@override_settings(OPENID={'mock': 'cvr'})
class TestDafoConnection(TestCase):

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
