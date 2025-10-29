import os
import re

from django.urls import reverse_lazy
from indberetning.utils import populate_dummy_session
from project.settings.base import strtobool

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# URLS for django login/logout used by administrators.
LOGIN_URL = reverse_lazy("administration:login")
LOGOUT_REDIRECT_URL = "administration:login"
LOGIN_REDIRECT_URL = "administration:postlogin"

# Must match namespace given to django_mitid_auth.urls in project/urls.py
LOGIN_NAMESPACE = "login"
LOGIN_MITID_URL = reverse_lazy("login:login")
LOGIN_PROVIDER_CLASS = os.environ.get("LOGIN_PROVIDER_CLASS") or None
LOGIN_MITID_REDIRECT_URL = reverse_lazy("indberetning:frontpage")
LOGOUT_MITID_REDIRECT_URL = reverse_lazy("indberetning:frontpage")

LOGIN_TIMEOUT_URL = reverse_lazy("indberetning:login-timeout")
LOGIN_REPEATED_URL = reverse_lazy("indberetning:login-repeat")
LOGIN_NO_CPRCVR_URL = reverse_lazy("indberetning:login-no-cvr")
LOGIN_ASSURANCE_LEVEL_URL = reverse_lazy("indberetning:login-assurance")
LOGIN_WHITELISTED_URLS = [
    "/favicon.ico",
    LOGIN_URL,
    re.compile("^/administration/"),
    re.compile("^/statistik/"),
    re.compile("^/media/"),
    re.compile("^/i18n/"),
    re.compile("^/metrics/"),
    re.compile("^/__debug__/"),
    "/_ht/",
    LOGIN_TIMEOUT_URL,
    LOGIN_REPEATED_URL,
    LOGIN_NO_CPRCVR_URL,
    LOGIN_ASSURANCE_LEVEL_URL,
]
MITID_TEST_ENABLED = bool(strtobool(os.environ.get("MITID_TEST_ENABLED", "False")))
SESSION_EXPIRE_SECONDS = int(os.environ.get("SESSION_EXPIRE_SECONDS") or 1800)
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_CALLABLE = "indberetning.utils.session_timed_out"
LOGIN_BYPASS_ENABLED = bool(strtobool(os.environ.get("LOGIN_BYPASS_ENABLED", "False")))
DEFAULT_CVR = os.environ.get("DEFAULT_CVR")
DEFAULT_CPR = None
POPULATE_DUMMY_SESSION = populate_dummy_session

SESSION_EXPIRE_AT_BROWSER_CLOSE = True


SAML = {
    "enabled": bool(strtobool(os.environ.get("SAML_ENABLED", "False"))),
    "debug": 1,
    "entityid": os.environ.get("SAML_SP_ENTITY_ID"),
    "idp_entity_id": os.environ.get("SAML_IDP_ENTITY_ID"),
    "name": os.environ.get("SAML_NAME") or "Aalisakkat",
    "description": os.environ.get("SAML_DESCRIPTION") or "Ressourcenter",
    "verify_ssl_cert": False,
    "metadata_remote": os.environ.get("SAML_IDP_METADATA"),
    "metadata": {"local": ["/var/cache/aalisakkat/idp_metadata.xml"]},  # IdP Metadata
    "service": {
        "sp": {
            "name": os.environ.get("SAML_NAME") or "Aalisakkat",
            "hide_assertion_consumer_service": False,
            "endpoints": {
                "assertion_consumer_service": [
                    (
                        os.environ.get("SAML_SP_LOGIN_CALLBACK_URI"),
                        "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
                    )
                ],
                "single_logout_service": [
                    (
                        os.environ.get("SAML_SP_LOGOUT_CALLBACK_URI"),
                        "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                    ),
                ],
            },
            "required_attributes": [
                "https://data.gov.dk/model/core/specVersion",
                "https://data.gov.dk/concept/core/nsis/loa",
                "https://data.gov.dk/model/core/eid/professional/orgName",
                "https://data.gov.dk/model/core/eid/fullName",
                "https://data.gov.dk/model/core/eid/professional/cvr",
            ],
            "optional_attributes": [
                "https://data.gov.dk/model/core/eid/cprNumber",
            ],
            "name_id_format": [
                "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
            ],
            "signing_algorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
            "authn_requests_signed": True,
            "want_assertions_signed": True,
            "want_response_signed": False,
            "allow_unsolicited": True,
            "logout_responses_signed": True,
        }
    },
    "key_file": os.environ.get("SAML_SP_KEY"),
    "cert_file": os.environ.get("SAML_SP_CERTIFICATE"),
    "encryption_keypairs": [
        {
            "key_file": os.environ.get("SAML_SP_KEY"),
            "cert_file": os.environ.get("SAML_SP_CERTIFICATE"),
        },
    ],
    "xmlsec_binary": "/usr/bin/xmlsec1",
    "delete_tmpfiles": True,
    "organization": {
        "name": [("Aalisakkat", "da")],
        "display_name": ["Aalisakkat"],
        "url": [("https://magenta.dk", "da")],
    },
    "contact_person": [
        {
            "given_name": os.environ["SAML_CONTACT_TECHNICAL_NAME"],
            "email_address": os.environ["SAML_CONTACT_TECHNICAL_EMAIL"],
            "type": "technical",
        },
        {
            "given_name": os.environ["SAML_CONTACT_SUPPORT_NAME"],
            "email_address": os.environ["SAML_CONTACT_SUPPORT_EMAIL"],
            "type": "support",
        },
    ],
    "preferred_binding": {
        "attribute_consuming_service": [
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
        ],
        "single_logout_service": [
            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
        ],
    },
}
