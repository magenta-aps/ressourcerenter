def session_timed_out(request):
    return None  # Let permissions middleware handle it


def populate_dummy_session():
    from django.conf import settings

    return {
        "cpr": settings.DEFAULT_CPR,
        "cvr": settings.DEFAULT_CVR,
        "organizationname": "Development Organization",
    }

