from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django_mitid_auth import login_provider_class


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._administrator_login_url = settings.LOGIN_URL
        self._administrator_logout_url = reverse("administration:logout")
        self._administrator_postlogin_url = reverse("administration:postlogin")
        self._indberetning_login_url = settings.LOGIN_MITID_URL
        self._indberetning_callback_url = reverse("login:login-callback")
        self.provider = login_provider_class()

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        :return: None means the user is allowed to access the view
        """
        # never redirect if we hit either login page:
        if request.path in (
            self._administrator_login_url,
            self._indberetning_login_url,
            self._indberetning_callback_url,
            self._administrator_logout_url,
            self._administrator_postlogin_url,
        ):
            return None

        if request.path == "/":
            # Redirects to indberetning (urls.py)
            return None

        app_name = request.resolver_match.app_name

        if app_name == "":
            if request.path.startswith("/media/"):
                # User may access media files
                return None
            if request.path.startswith("/i18n/"):
                # User may access language functions
                return None
            if request.path.startswith("/_ht/"):
                # User may access monitoring
                return None
            if request.path.startswith("/error/"):
                # User may access error pages
                return None
            else:
                raise PermissionDenied
        elif app_name == "djdt":
            return None
        elif app_name in (
            "mitid_test",
            "django_mitid_auth",
            "django_mitid_auth:django_mitid_auth.saml",
        ):
            return None
        elif app_name == "indberetning":
            if request.path.startswith("/indberetning/error/"):
                return None
            if not self.provider.is_logged_in(request):
                # nemId user not logged in so redirect to login page
                return redirect(self._indberetning_login_url)
        else:
            if not request.user.is_authenticated:
                path = request.get_full_path()
                # user not logged in, but trying to access a page they must be logged in for.
                return redirect_to_login(path, self._administrator_login_url, "next")
            if not request.user.groups.filter(
                name=request.resolver_match.app_name
            ).exists():
                # User is logged in, but has insufficient permissions
                raise PermissionDenied
