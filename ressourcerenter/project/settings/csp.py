import os
from csp.constants import NONCE, SELF
from project.settings.base import DEBUG

HOST_DOMAIN = os.environ.get("HOST_DOMAIN", "https://aalisakkat.aka.sullissivik.gl")

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [
            SELF,
            NONCE,
            "localhost:8000" if DEBUG else HOST_DOMAIN,
        ],
        "script-src-attr": [
            SELF,
            NONCE,
            "localhost:8000" if DEBUG else HOST_DOMAIN,
        ],
        "style-src-elem": [
            SELF,
            NONCE,
            "localhost:8000" if DEBUG else HOST_DOMAIN,
        ],
        "style-src-attr": [SELF, NONCE],
        "img-src": [
            SELF,
            NONCE,
            "data:",
        ],
    },
}
