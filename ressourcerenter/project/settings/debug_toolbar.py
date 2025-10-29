import os

from project.settings.base import DEBUG, strtobool

if DEBUG:
    import socket

    hostname, foo, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]


def show_toolbar(request):
    return strtobool(os.environ.get("SHOW_DEBUG_TOOLBAR", "False"))


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}
