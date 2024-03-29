
from django.test import TestCase, override_settings
from project.dafo import DatafordelerClient


@override_settings(DAFO={'mock': True})
class TestDafoConnection(TestCase):

    def test_lookup_company_info(self):
        """
        Call the dafo-client to get a companyinfo
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_company_information('12950160')
        self.assertEqual({
            "source": "CVR",
            "cvrNummer": 12950160,
            "navn": "Magenta Grønland ApS",
            "myndighedskode": 956,
            "adresse": "Imaneq 32A, 3.",
            "postnummer": 3900,
            "bynavn": "Nuuk",
            "landekode": "GL"
        }, result)

    def test_lookup_person_info(self):
        """
        Call the dafo-client to get a personinfo
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_person_information('1111111111')
        self.assertEqual({
            "cprNummer": "1111111111",
            "fornavn": "Anders",
            "efternavn": "And",
            "statsborgerskab": 5100,
            "myndighedskode": 957,
            "adresse": "Imaneq 32A, 3.",
            "postnummer": 3900,
            "landekode": "GL"
        }, result)

    def test_lookup_person_ownerinfo(self):
        """
        Call the dafo-client to get a personinfo
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_owner_information('1234567890')
        self.assertEqual([
            12345678
        ], result)
