import logging
from urllib.parse import urljoin
from requests import Session
import requests
from requests import RequestException
from django.conf import settings

logger = logging.getLogger(__name__)


class DatafordelerClient(object):
    combined_service_page_size = 400

    def __init__(self, mock=None, client_header=None, service_header_cvr=None, service_header_cpr=None, certificate=None, root_ca=None, private_key=None, url=None, verify=True, timeout=60):

        self._mock = mock
        self._client_header = None
        self._service_header_cvr = None
        self._service_header_cpr = None
        self._cert = None
        self._pitu_root_ca = None
        self._pitu_url = None
        self._timeout = False

        if not self._mock:
            self._client_header = client_header
            self._service_header_cvr = service_header_cvr
            self._service_header_cpr = service_header_cpr
            self._cert = (certificate, private_key)
            self._root_ca = root_ca
            self._private_key = private_key
            self._url = url
            self._verify = verify
            self._timeout = timeout
            self._session = Session()
            self._session.headers.update({'Uxp-Client': client_header})

    def __del__(self):
        if hasattr(self, '_session'):
            self._session.close()

    @classmethod
    def from_settings(cls):
        return cls(mock=settings.DAFO['mock'], client_header=settings.DAFO.get('uxp_client'),
                   service_header_cvr=settings.DAFO.get('uxp_service_cvr'), service_header_cpr=settings.DAFO.get('uxp_service_cpr'),
                   certificate=settings.DAFO.get('certificate'), root_ca=settings.DAFO.get('root_ca'),
                   private_key=settings.DAFO.get('key'), url=settings.DAFO.get('url'))

    def get_company_information(self, cvr):
        """
        Lookup address information for cvr
        """
        if self._mock:
            return {
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
            }
        else:
            return self.get(cvr, self._service_header_cvr)

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
                "køn": "K",
                "statuskode": 1,
                "statuskodedato": "2017-01-23",
                "tilflytningsdato": "2020-10-27",
                "myndighedskode": 957,
                "vejkode": 281,
                "kommune": "Qeqqata Kommunia",
                "postnummer": 3900,
                "stedkode": 600,
                "landekode": "GL"
            }
        else:
            return self.get(cpr, self._service_header_cpr)

    def get(self, number, service_header):
        headers = {'Uxp-Service': service_header,
                   'Uxp-Client': self._client_header}
        try:
            url = urljoin(self._url, number)
            r = requests.get(url, cert=self._cert, verify=self._root_ca, timeout=self._timeout,
                             headers=headers)
            # raises 404 if cpr is invalid
            r.raise_for_status()
        except RequestException as e:
            if not getattr(e, 'response', None) or e.response.status_code != 404:
                #  Do not log 404s, invalid CPR numbers
                logger.exception(e)
            raise
        else:
            return r.json()

    def get_owned_companies(self, cpr):
        """
        Should return a list of companies there might need some definition
        """
        if self._mock:
            return {'12345678': '12345678'}
        pass
