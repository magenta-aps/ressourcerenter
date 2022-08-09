from django.test import TestCase, override_settings
from project.dafo import DatafordelerClient


@override_settings(DAFO={"mock": True})
class TestDafoConnection(TestCase):
    def test_lookup_company_info(self):
        """
        Call the dafo-client to get a companyinfo
        """
        dafo_client = DatafordelerClient.from_settings()
        result = dafo_client.get_company_information("12950160")
        self.assertEqual(
            {
                "source": "CVR",
                "cvrNummer": 12950160,
                "navn": "Magenta Grønland ApS",
                "myndighedskode": 956,
                "adresse": "Imaneq 32A, 3.",
                "postnummer": 3900,
                "bynavn": "Nuuk",
                "landekode": "GL",
                "stedkode": 600,
            },
            result,
        )
