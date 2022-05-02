from urllib.parse import urljoin
from requests import Session
from django.conf import settings


class DatafordelerClient(object):
    combined_service_page_size = 400

    def __init__(self, mock=None, client_header=None, service_header_cvr=None,
                 certificate=None, private_key=None, url=None, root_ca=True, timeout=10):

        self._mock = mock

        if not self._mock:
            self._client_header = client_header
            self._service_header_cvr = service_header_cvr
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
                "landekode": "GL",
                "stedkode": 600,
            }
        else:
            return self._get(str(cvr).zfill(8), self._service_header_cvr)

    def _get(self, number, service_header):
        url = urljoin(self._url, number)
        r = self._session.get(url, cert=self._cert, verify=self._root_ca, timeout=self._timeout,
                              headers={'Uxp-Service': service_header})
        r.raise_for_status()
        return r.json()
