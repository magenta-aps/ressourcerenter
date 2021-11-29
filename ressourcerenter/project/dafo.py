import logging
from urllib.parse import urljoin
from requests import Session
import requests
from requests import RequestException
from django.conf import settings

logger = logging.getLogger(__name__)


class DatafordelerClient(object):
    combined_service_page_size = 400

    def __init__(self, mock=None, client_header=None, service_header_cvr=None, service_header_cpr=None, certificate=None, pitu_root_ca=None, private_key=None, pitu_url=None, verify=True, timeout=60):

        self._mock = mock
        self._client_header = None
        self._service_header_cvr = None
        self._service_header_cpr = None
        self._cert = None
        self._pitu_root_ca = None
        self._pitu_url = None
        self._client_has_mock_enabled = True
        self._timeout = False

        if not self._mock:
            self._client_has_mock_enabled = False
            self._client_header = client_header
            self._service_header_cvr = service_header_cvr
            self._service_header_cpr = service_header_cpr
            self._cert = (certificate, private_key)
            self._pitu_root_ca = pitu_root_ca
            self._private_key = private_key
            self._pitu_url = pitu_url

            self._verify = verify
            self._timeout = timeout
            self._session = Session()
            self._session.headers.update({'Uxp-Client': client_header})

    def __del__(self):
        if hasattr(self, '_session'):
            self._session.close()

    @classmethod
    def from_settings(cls):
        return cls(mock=settings.DAFO['pitu_mock'], client_header=settings.DAFO.get('pitu_uxp_client'),
                   service_header_cvr=settings.DAFO.get('pitu_uxp_service_cvr'), service_header_cpr=settings.DAFO.get('pitu_uxp_service_cpr'),
                   certificate=settings.DAFO.get('pitu_certificate'), pitu_root_ca=settings.DAFO.get('pitu_root_ca'),
                   private_key=settings.DAFO.get('pitu_key'), pitu_url=settings.DAFO.get('pitu_url'))

    def get_company_information(self, cvr):
        """
        Lookup address information for cvr
        """
        return self.get_address_and_name_for_cvr(cvr)

    def get(self, number, service_header):
        headers = {'Uxp-Service': service_header,
                   'Uxp-Client': self._client_header}
        try:
            url = urljoin(self._pitu_url, '{number}/'.format(number=number))
            r = requests.get(url, cert=self._cert, verify=self._pitu_root_ca, timeout=self._timeout,
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

    def extract_address_and_name_from_cpr_response(self, data_dict):
        for field in ('fornavn', 'efternavn', 'adresse', 'postnummer', 'bynavn', 'landekode'):
            # avoid key errors by adding '' as default value since every field is optional
            if field not in data_dict:
                data_dict[field] = ''
        return {'name': '{fornavn} {efternavn}'.format(**data_dict),
                'address': '{adresse}\n{postnummer} {bynavn}'.format(**data_dict),
                'country': '{landekode}'.format(**data_dict)}

    def extract_address_and_company_from_cvr_response(self, data_dict):
        for field in ('adresse', 'postnummer', 'bynavn', 'landekode'):
            if field not in data_dict:
                data_dict[field] = ''
        return {'name': data_dict.get('navn', ''),
                'address': '{adresse}\n{postnummer} {bynavn}'.format(**data_dict),
                'country': '{landekode}'.format(**data_dict)}

    def get_address_and_name_for_cpr(self, number):
        if not self._client_has_mock_enabled:
            response = self.get(number, self._service_header_cpr)
        else:
            response = {"fornavn": "fornavn", "efternavn": "efternavn", "adresse": "adresse", "postnummer": "0000", "landekode": "GL"}
        return self.extract_address_and_name_from_cpr_response(response)

    def get_address_and_name_for_cvr(self, number):
        if not self._client_has_mock_enabled:
            response = self.get(number, self._service_header_cvr)
        else:
            response = {"navn": "navn", "adresse": "adresse", "postnummer": "0000", "landekode": "GL"}
        return self.extract_address_and_company_from_cvr_response(response)

    def get_address_and_name(self, number, number_type):
        if number_type == 'cpr':
            return self.get_address_and_name_for_cpr(number)
        elif number_type == 'cvr':
            return self.get_address_and_name_for_cvr(number)

    def get_owned_companies(self, cpr):
        """
        Should return a list of companies there might need some definition
        """
        if self._mock:
            return {'12345678': '12345678'}
        pass
