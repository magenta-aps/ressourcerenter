import logging

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

logger = logging.getLogger(__name__)

"""
Borrows heavily from python3-saml-django
https://pypi.org/project/python3-saml-django/
"""
class Saml2:

    @property
    def name(self):
        return 'saml2'

    session_keys = ('saml')

    @classmethod
    def from_settings(cls):
        return cls(**settings.SAML)

    claims_map = {
        'PersonName': 'http://schemas.microsoft.com/identity/claims/displayname',
    }

    @staticmethod
    def user_is_logged_in(request):
        """
        checks if the user is "logged in"
        """
        return 'saml' in request.session

    @staticmethod
    def _clear_secrets(session):
        for key in Saml2.session_keys:
            if key in session:
                del session[key]


    def metadata(self, request):
        """Render the metadata of this service."""
        metadata_dict = settings.ONELOGIN_SAML_SETTINGS.get_sp_metadata()
        errors = settings.ONELOGIN_SAML_SETTINGS.validate_metadata(metadata_dict)
        if len(errors) == 0:
            resp = HttpResponse(content=metadata_dict, content_type='text/xml')
        else:
            resp = HttpResponseServerError(content=', '.join(errors))
        return resp

    def login(self, request):
        """Kick off a SAML login request."""
        req = self._prepare_django_request(request)
        saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
        if 'next' in request.GET:
            redirect_to = OneLogin_Saml2_Utils.get_self_url(req) + request.GET['next']
        else:
            redirect_to = OneLogin_Saml2_Utils.get_self_url(req) + settings.SAML_LOGIN_REDIRECT
        url = saml_auth.login(redirect_to)
        request.session['AuthNRequestID'] = saml_auth.get_last_request_id()
        return HttpResponseRedirect(url)

    def handle_login_callback(self, request, success_url, failure_url):
        """Handle an AuthenticationResponse from the IdP."""
        if request.method != 'POST':
            return HttpResponse('Method not allowed.', status=405)
        try:
            req = self._prepare_django_request(request)
            saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)

            request_id = request.session.get('AuthNRequestID', None)
            saml_auth.process_response(request_id=request_id)

            errors = saml_auth.get_errors()

            if not errors:
                request.session['saml'] = {
                    'nameId': saml_auth.get_nameid(),
                    'nameIdFormat': saml_auth.get_nameid_format(),
                    'nameIdNameQualifier': saml_auth.get_nameid_nq(),
                    'nameIdSPNameQualifier': saml_auth.get_nameid_spnq(),
                    'sessionIndex': saml_auth.get_session_index(),
                }
                saml_claims = saml_auth.get_attributes()
                request.session['user_info'] = {
                    key: saml_claims[claimKey][0]
                    for key, claimKey in self.claims_map.items()
                    if claimKey in saml_claims
                }
                request.session['cvr'] = request.session['user_info'].get('CVR')
                # This data is used during Single Log Out

                if 'RelayState' in req['post_data'] \
                        and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
                    url = saml_auth.redirect_to(req['post_data']['RelayState'])
                    return HttpResponseRedirect(url)
                else:
                    return HttpResponseRedirect(success_url)
            logger.exception(saml_auth.get_last_error_reason())
            return HttpResponse(content="Invalid Response", status=400)
        except PermissionDenied:
            raise
        except Exception as e:
            logger.exception(e)
            return HttpResponse(content="Invalid Response", status=400)

    def logout(self, request):
        """Kick off a SAML logout request."""
        req = self._prepare_django_request(request)
        saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
        (name_id, session_index, name_id_format, name_id_nq, name_id_spnq) = (None, None, None, None, None)
        saml_session = request.session.get('saml', None)
        if saml_session:
            name_id = saml_session.get('nameId', None)
            session_index = saml_session.get('sessionIndex', None)
            name_id_format = saml_session.get('nameIdFormat', None)
            name_id_nq = saml_session.get('nameIdNameQualifier', None)
            name_id_spnq = saml_session.get('nameIdSPNameQualifier', None)
        auth.logout(request)
        url = saml_auth.logout(
            name_id=name_id, session_index=session_index, nq=name_id_nq, name_id_format=name_id_format, spnq=name_id_spnq,
            return_to=OneLogin_Saml2_Utils.get_self_url(req) + settings.SAML_LOGOUT_REDIRECT
        )
        request.session['LogoutRequestID'] = saml_auth.get_last_request_id()
        return HttpResponseRedirect(url)

    def handle_logout_callback(self, request):
        """Handle a LogoutResponse from the IdP."""
        if request.method != 'GET':
            return HttpResponse('Method not allowed.', status=405)
        req = self._prepare_django_request(request)
        saml_auth = OneLogin_Saml2_Auth(req, old_settings=settings.ONELOGIN_SAML_SETTINGS)
        request_id = request.session.get('LogoutRequestID', None)
        try:
            url = saml_auth.process_slo(request_id=request_id, delete_session_cb=lambda: request.session.flush())
            errors = saml_auth.get_errors()
            if len(errors) == 0:
                auth.logout(request)
                redirect_to = url or settings.SAML_LOGOUT_REDIRECT
                return HttpResponseRedirect(redirect_to)
            else:
                logger.exception(saml_auth.get_last_error_reason())
                return HttpResponse("Invalid request", status=400)
        except UnicodeDecodeError:
            # Happens when someone messes with the response in the URL.  No need to log an exception.
            return HttpResponse("Invalid request - Unable to decode response", status=400)
        except Exception as e:
            logger.exception(e)
            return HttpResponse("Invalid request", status=400)

    def metadata(self, request):
        """Render the metadata of this service."""
        metadata_dict = settings.ONELOGIN_SAML_SETTINGS.get_sp_metadata()
        errors = settings.ONELOGIN_SAML_SETTINGS.validate_metadata(metadata_dict)

        if len(errors) == 0:
            resp = HttpResponse(content=metadata_dict, content_type='text/xml')
        else:
            resp = HttpResponseServerError(content=', '.join(errors))
        return resp

    def _prepare_django_request(self, request):
        """Extract data from a Django request in the way that OneLogin expects."""
        result = {
            'https': 'on' if request.is_secure() else 'off',
            'http_host': request.META.get('HTTP_HOST', '127.0.0.1'),
            'script_name': request.META['PATH_INFO'],
            'server_port': request.META['SERVER_PORT'],
            'get_data': request.GET.copy(),
            'post_data': request.POST.copy()
        }
        if settings.SAML_DESTINATION_HOST is not None:
            result['http_host'] = settings.SAML_DESTINATION_HOST
        if settings.SAML_DESTINATION_HTTPS is not None:
            result['https'] = settings.SAML_DESTINATION_HTTPS
            result['server_port'] = '443' if result['https'] else '80'
        if settings.SAML_DESTINATION_PORT is not None:
            result['server_port'] = settings.SAML_DESTINATION_PORT
        return result

class OIOSaml(Saml2):

    @property
    def name(self):
        return 'oiosaml'

    # Maps session['user_info'] keys to SAML claims
    claims_map = {
        'CVR': 'https://data.gov.dk/model/core/eid/professional/cvr',
        'CPR': 'https://data.gov.dk/model/core/eid/cprNumber',
        'PersonName': 'https://data.gov.dk/model/core/eid/fullName',
        'OrganizationName': 'https://data.gov.dk/model/core/eid/professional/orgName',
    }
