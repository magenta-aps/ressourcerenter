
from django.test import TestCase, override_settings
from project.dafo import DatafordelerClient


@override_settings(DAFO={'pitu_mock': True})
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
            "forretningsområde": "Computerprogrammering",
            "statuskode": "NORMAL",
            "statuskodedato": "2017-11-01",
            "myndighedskode": 956,
            "kommune": "SERMERSOOQ",
            "vejkode": 102,
            "stedkode": 600,
            "adresse": "Imaneq 32A, 3.",
            "postboks": 924,
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
            "civilstand": "U",
            "statsborgerskab": 5100,
            "køn": "K",
            "statuskode": 1,
            "statuskodedato": "2017-01-23",
            "tilflytningsdato": "2020-10-27",
            "myndighedskode": 957,
            "vejkode": 281,
            "kommune": "Qeqqata Kommunia",
            "postnummer": 0,
            "stedkode": 0,
            "landekode": "GL"
        }, result)
