from requests import Session
from django.conf import settings


class DatafordelerClient(object):
    combined_service_page_size = 400

    def __init__(self, mock=None, client_header=None, certificate=None, private_key=None, verify=True, timeout=60):
        self._mock = mock
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
            # TODO figure out what dafo returns
            return {'address': 'test address'}
        pass

    def get_owned_companies(self, cpr):
        """
        Should return a list of companies owned by cpr
        """
        if self._mock:
            return {'12345678': {'address': 'test address'}}
        pass
