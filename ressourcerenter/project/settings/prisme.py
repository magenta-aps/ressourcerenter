import os

from project.settings.base import strtobool

PRISME = {
    "wsdl_file": os.environ.get("PRISME_PULL_WSDL", ""),
    "auth": {
        "basic": {
            "username": os.environ.get("PRISME_PULL_USERNAME", ""),
            "domain": os.environ.get("PRISME_PULL_DOMAIN", ""),
            "password": os.environ.get("PRISME_PULL_PASSWORD", ""),
        }
    },
    "proxy": {"socks": os.environ.get("PRISME_SOCKS_PROXY")},
}

PRISME_PUSH = {
    "mock": strtobool(os.environ.get("PRISME_PUSH_MOCK", "false")),
    "host": os.environ.get("PRISME_PUSH_HOST"),
    "port": int(os.environ.get("PRISME_PUSH_PORT") or 22),
    "username": os.environ.get("PRISME_PUSH_USERNAME"),
    "password": os.environ.get("PRISME_PUSH_PASSWORD"),
    "known_hosts": os.environ.get("PRISME_PUSH_KNOWN_HOSTS") or None,
    "dirs": {
        "10q_production": os.environ.get("PRISME_PUSH_DEST_PROD_PATH"),
        "10q_development": os.environ.get("PRISME_PUSH_DEST_TEST_PATH"),
    },
    "destinations_available": {
        "10q_production": strtobool(
            os.environ.get("PRISME_PUSH_DEST_PROD_AVAILABLE", "false")
        ),
        "10q_development": strtobool(
            os.environ.get("PRISME_PUSH_DEST_TEST_AVAILABLE", "true")
        ),
    },
    "fielddata": {
        # System-identificerende streng der kommer på transaktioner i Prisme. Max 4 tegn
        "project_id": os.environ.get("PRISME_PUSH_PROJECT_ID"),
        # Brugernummer der kommer på transaktioner i Prisme. Max 4 tegn
        "user_number": os.environ.get("PRISME_PUSH_USER_NUMBER", "0900"),
        # Betalingsart der kommer på transaktioner i Prisme. Max 3 tegn
        "payment_type": int(os.environ.get("PRISME_PUSH_PAYMENT_TYPE") or 0),
        # Kontonummer der danner bro i Prisme SEL
        "account_number": int(os.environ.get("PRISME_PUSH_ACCOUNT_NUMBER") or 0),
    },
}
