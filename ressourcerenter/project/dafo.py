import logging
from urllib.parse import urljoin
from requests import Session
import requests
from requests import RequestException
from django.conf import settings

logger = logging.getLogger(__name__)


class DatafordelerClient(object):
    combined_service_page_size = 400

    def __init__(self, mock=None, client_header=None, certificate=None, private_key=None, verify=True, timeout=60):
        self._mock = mock
        self._client_header = client_header

        if self._mock is False:
            self._cert = (certificate, private_key)
            self._verify = verify
            self._timeout = timeout
            self._session = Session()
            self._session.headers.update({'Uxp-Client': client_header})

    def __del__(self):
        if hasattr(self, '_session'):
            self._session.close()

    @classmethod
    def from_settings(cls):
        return cls(settings.DAFO)

    def get_company_information(self, cvr):
        """
        Lookup address information for cvr
        """
        if self._mock:
            return {'name': 'test company_name'}
        else:
            return self.get_address_and_name_for_cvr(cvr)

    def get_owned_companies(self, cpr):
        """
        Should return a list of companies owned by cpr, it is still undefined if we need this functionality
        """
        return {'12345678': {'not_implemented': 'not_implemented'}}

    def get(self, url, service_header):
        headers = {'Uxp-Service': service_header,
                   'Uxp-Client': settings.PITU.get('client_header')}
        try:
            r = requests.get(url, cert=self.cert, verify=self.root_ca, timeout=self._timeout,
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
        data_dict['country'] = self.get_country(data_dict.get('myndighedskode', None))
        for field in ('fornavn', 'efternavn', 'adresse', 'postnummer', 'bynavn'):
            # avoid key errors by adding '' as default value since every field is optional
            if field not in data_dict:
                data_dict[field] = ''
        return {'name': '{fornavn} {efternavn}'.format(**data_dict),
                'address': '{adresse}\n{postnummer} {bynavn}\n{country}'.format(**data_dict)}

    def extract_address_and_company_from_cvr_response(self, data_dict):
        data_dict['country'] = self.get_country(data_dict.get('myndighedskode', None))
        for field in ('adresse', 'postnummer', 'bynavn'):
            if field not in data_dict:
                data_dict[field] = ''
        return {'name': data_dict.get('navn', ''),
                'address': '{adresse}\n{postnummer} {bynavn}\n{country}'.format(**data_dict)}

    def get_address_and_name_for_cpr(self, number):
        if self.enabled is False or self._cpr_service.get('enabled', False) is False:
            return {}
        url = urljoin(self._cpr_service.get('url'), '{number}/'.format(number=number))
        return self.extract_address_and_name_from_cpr_response(self.get(url, self._cpr_service['header']))

    def get_address_and_name_for_cvr(self, number):
        if self.enabled is False or self._cvr_service.get('enabled', False) is False:
            return {}
        url = urljoin(self._cvr_service.get('url'), '{number}/'.format(number=number))
        return self.extract_address_and_company_from_cvr_response(self.get(url, self._cvr_service['header']))

    def get_address_and_name(self, number, number_type):
        if number_type == 'cpr':
            return self.get_address_and_name_for_cpr(number)
        elif number_type == 'cvr':
            return self.get_address_and_name_for_cvr(number)
