import logging

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.urls import reverse
from jwkest.jwk import rsa_load
from oic.oauth2 import ErrorResponse
from oic.oic import Client, rndstr
from oic.oic.message import AuthorizationResponse, RegistrationResponse
from oic.utils.authn.client import CLIENT_AUTHN_METHOD
from oic.utils.keyio import KeyBundle, KeyJar

logger = logging.getLogger(__name__)


class OpenId:

    @property
    def name(self):
        return 'openid'

    def __init__(self, mock=None, scope=None, client_id=None, private_key=None, certificate=None, issuer=None,
                 front_channel_logout_uri=None, post_logout_redirect_uri=None,
                 logout_uri=None, login_callback_url=None):
        self._mock = mock
        if not mock:
            self._scope = scope
            self._client_id = client_id
            self._issuer = issuer
            self._front_channel_logout_uri = front_channel_logout_uri
            self._post_logout_redirect_uri = post_logout_redirect_uri
            self._logout_uri = logout_uri
            self._login_callback_url = login_callback_url

            # private_key and certificate needs to be a path
            rsa_key = rsa_load(private_key)
            kj = KeyJar()
            kj[""] = KeyBundle([{'key': rsa_key, 'kty': 'RSA', 'use': 'ver'},
                                {'key': rsa_key, 'kty': 'RSA', 'use': 'sig'}])

            self._oic_client = Client(
                client_authn_method=CLIENT_AUTHN_METHOD,
                client_cert=(certificate, private_key),
                keyjar=kj
            )

    @classmethod
    def from_settings(cls):
        return cls(**settings.OPENID)

    @staticmethod
    def clear_session(session):
        for key in ['oid_state', 'oid_nonce', 'user_info',
                    'login_method', 'sid', 'cvr', 'cpr',
                    'company_information', 'companies']:
            if key in session:
                del session[key]
        session.save()

    @staticmethod
    def user_is_logged_in(request):
        """
        checks if the user is "logged in"
        """
        return request.session.get('cpr', '') != ''

    def login(self, request):
        """
        Setup the session and redirect the user to the oauth login page
        :param request: the current request
        :return: should return the redirect url for the external system
        """
        if self._mock:
            request.session['oid_state'] = rndstr(32)
            request.session['oid_nonce'] = rndstr(32)
            return reverse('indberetning:login-callback')

        provider_info = self._oic_client.provider_config(self._issuer)  # noqa
        client_reg = RegistrationResponse(**{
            'client_id': self._client_id,
            'redirect_uris': [self._login_callback_url]
        })
        self._oic_client.store_registration_info(client_reg)

        state = rndstr(32)
        nonce = rndstr(32)
        request_args = {
            'response_type': 'code',
            'scope': self._scope,
            'client_id': self._client_id,
            'redirect_uri': self._login_callback_url,
            'state': state,
            'nonce': nonce
        }
        request.session['oid_state'] = state
        request.session['oid_nonce'] = nonce
        auth_req = self._oic_client.construct_AuthorizationRequest(request_args=request_args)
        return auth_req.request(self._oic_client.authorization_endpoint)

    @staticmethod
    def _clear_secrets(session):
        for key in ('oid_state', 'oid_nonce'):
            if key in session:
                del session[key]

    @staticmethod
    def _validate_session(session):
        """
        validate that the session contains the needed shared secrets.
        :return: True/False
        """
        if session.get('oid_state') and session.get('oid_nonce'):
            return True
        else:
            if session.get('oid_state') is None and session.get('oid_nonce') is None:
                logger.exception(SuspiciousOperation('Both oid_state and oid_nonce is missing from session'))
            else:
                for key in ('oid_state', 'oid_nonce'):
                    if key not in session:
                        logger.exception(SuspiciousOperation('Session %s does not exist!', key))
            return False

    def _validate_authorization_response(self, request):
        auth_response = self._oic_client.parse_response(AuthorizationResponse, info=request.META['QUERY_STRING'], sformat="urlencoded")
        if isinstance(auth_response, ErrorResponse):
            logger.error("Got ErrorResponse from openID %s" % str(auth_response.to_dict()))
            return None
        elif auth_response.get('state') is None or auth_response['state'] != request.session['oid_state']:
            logger.exception(SuspiciousOperation('Session `oid_state` does not match the OID callback state'))
            return None
        return auth_response

    @staticmethod
    def _validate_access_token_response(access_token_response, session):
        if isinstance(access_token_response, ErrorResponse):
            logger.error('Error received from headnet: {}'.format(str(ErrorResponse)))
            return None
        access_token_dictionary = access_token_response.to_dict()
        their_nonce = access_token_dictionary['id_token']['nonce']
        if their_nonce != session['oid_nonce']:
            logger.error("Nonce mismatch: Token service responded with incorrect nonce (expected %s, got %s)" % (session['oid_nonce'], their_nonce))
            return None
        return access_token_dictionary

    def handle_login_callback(self, request):
        """
        Handle the oauth callback after the user logged in.
        Should populate the session with claims data such as cpr and cvr number.
        :param request: the current request
        :return: True if the user logged in correctly
                 false if the session was not recognized or any problem occurs
        """
        if self._validate_session(request.session):
            if self._mock in ('cpr', 'cvr'):
                self._clear_secrets(request.session)
                if self._mock == 'cpr':
                    request.session['cpr'] = '123456-1955'
                elif self._mock == 'cvr':
                    request.session['cpr'] = '123456-1955'
                    request.session['cvr'] = '12345678'
                return True

            self._oic_client.store_registration_info({'client_id': self._client_id,
                                                      'token_endpoint_auth_method': 'private_key_jwt'})
            authorization_response = self._validate_authorization_response(request)
            if authorization_response:
                provider_info = self._oic_client.provider_config(self._issuer)
                logger.debug('provider info: {}'.format(provider_info))
                access_token_response = self._oic_client.do_access_token_request(
                    state=authorization_response['state'],
                    scope=self._scope,
                    request_args={'code': authorization_response['code'],
                                  'redirect_uri': self._login_callback_url},
                    authn_method="private_key_jwt",
                    authn_endpoint='token'
                )
                access_token_dictionary = self._validate_access_token_response(access_token_response, request.session)
                if access_token_dictionary:
                    userinfo = self._oic_client.do_user_info_request(state=request.session['oid_state'])
                    request.session['user_session'] = userinfo.to_dict()
                    # needed for logout
                    request.session['id_token'] = access_token_dictionary['id_token']
                    request.session['raw_id_token'] = access_token_response['id_token'].jwt
                    self._clear_secrets(request.session)
                    return True
        self._clear_secrets(request.session)
        return False

    def logout(self, request):
        if self._mock:
            self.clear_session(request.session)
            return reverse('indberetning:logout-callback')
        self._oic_client.store_registration_info(
            RegistrationResponse(**{
                'client_id': self._client_id,
                'redirect_uris': [self._front_channel_logout_uri],
                'post_logout_redirect_uris': [self._post_logout_redirect_uri]
            })
        )

        auth_req = self._oic_client.construct_EndSessionRequest(
            request_args={
                'scope': self._scope,
                'client_id': self._client_id,
                'redirect_uri': self._front_channel_logout_uri,
                'id_token_hint': request.session.get('raw_id_token'),
                'post_logout_redirect_uri': self._post_logout_redirect_uri,
                'state': rndstr(32)
            },
            id_token=request.session['id_token']
        )
        logout_url = auth_req.request(self._logout_uri)
        self.clear_session(request.session)
        return logout_url

    def handle_logout_callback(self, request):
        if self._mock:
            return
        their_sid = request.GET.get('sid')
        our_sid = request.session.get('id_token', {}).get('sid', None)
        if their_sid is None or our_sid is None or their_sid != our_sid:
            logger.error(SuspiciousOperation('sid for logout do not match our_sid: %s, their_sid: %s' % (our_sid,
                                                                                                         their_sid)))
            return
        # according to the specs this is rendered in a iframe when the user triggers a logout from OP`s side
        # do a total cleanup and delete everything related to openID
        self.clear_session(request.session)
