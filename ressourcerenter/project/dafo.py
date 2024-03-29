from urllib.parse import urljoin
from requests import Session
from django.conf import settings


class DatafordelerClient(object):
    combined_service_page_size = 400

    def __init__(self, mock=None, client_header=None, service_header_cvr=None,
                 service_header_cpr=None, uxp_service_owned_by=None,
                 certificate=None, private_key=None, url=None, root_ca=True, timeout=60):

        self._mock = mock

        if not self._mock:
            self._client_header = client_header
            self._service_header_cvr = service_header_cvr
            self._service_header_cpr = service_header_cpr
            self._uxp_service_owned_by = uxp_service_owned_by
            self._cert = (certificate, private_key)
            self._root_ca = root_ca
            self._url = url
            self._root_ca = root_ca
            self._timeout = timeout
            self._session = Session()
            self._session.headers.update({'Uxp-Client': client_header})

    def __del__(self):
        if hasattr(self, '_session'):
            self._session.close()

    @classmethod
    def from_settings(cls):
        return cls(**settings.DAFO)

    def get_company_information(self, cvr):
        """
        Lookup address information for cvr
        """
        if self._mock:
            return {
                "source": "CVR",
                "cvrNummer": 12950160,
                "navn": "Magenta Grønland ApS",
                "myndighedskode": 956,
                "adresse": "Imaneq 32A, 3.",
                "postnummer": 3900,
                "bynavn": "Nuuk",
                "landekode": "GL"
            }
        else:
            return self._get(cvr, self._service_header_cvr)

    def get_person_information(self, cpr):
        """
        Lookup address information for cpr
        """
        if self._mock:
            return {
                "cprNummer": "1111111111",
                "fornavn": "Anders",
                "efternavn": "And",
                "statsborgerskab": 5100,
                "myndighedskode": 957,
                "adresse": "Imaneq 32A, 3.",
                "postnummer": 3900,
                "landekode": "GL"
            }
        else:
            return self._get(cpr, self._service_header_cpr)

    def get_owner_information(self, cpr):
        """
        Lookup owner information for cpr
        """
        if self._mock:
            return [
                12345678
            ]
        else:
            return self._get(cpr, self._uxp_service_owned_by)

    def get_stedkoder(self):
        url = 'https://dafo.test.data.gl/geo/locality/1/rest/search?pageSize=1000'
        response = self._session.get(url, timeout=self._timeout, headers={'Accept': "application/json"})
        response.raise_for_status()
        return response.json()['results']

    def _get(self, number, service_header):
        url = urljoin(self._url, number)
        r = self._session.get(url, cert=self._cert, verify=self._root_ca, timeout=self._timeout,
                              headers={'Uxp-Service': service_header})
        r.raise_for_status()
        return r.json()
