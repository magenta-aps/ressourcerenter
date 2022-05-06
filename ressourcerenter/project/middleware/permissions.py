from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.module_loading import import_string


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._administrator_login_url = reverse(settings.LOGIN_URL)
        self._indberetning_login_url = reverse('indberetning:login')
        self._administrator_logout_url = reverse('administration:logout')
        self._administrator_postlogin_url = reverse('administration:postlogin')
        self._indberetning_callback_url = reverse('indberetning:login-callback')
        self._indberetning_metadata_url = reverse('indberetning:metadata')
        login_provider = import_string(settings.LOGIN_PROVIDER_CLASS)
        self._login_provider = login_provider.from_settings()

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        :return: None means the user is allowed to access the view
        """
        # never redirect if we hit either login page:
        if request.path in (self._administrator_login_url,
                            self._indberetning_login_url,
                            self._indberetning_callback_url,
                            self._indberetning_metadata_url,
                            self._administrator_logout_url,
                            self._administrator_postlogin_url,
                            ):
            return None

        app_name = request.resolver_match.app_name

        if app_name == 'indberetning':
            if self._login_provider.user_is_logged_in(request) is False:
                # nemId user not logged in so redirect to login page
                return redirect(self._indberetning_login_url)
        else:
            if not request.user.is_authenticated:
                # user not logged in, but trying to access a page they must be logged in for.
                return redirect_to_login(request.get_full_path(), self._administrator_login_url, 'next')

            if not request.user.groups.filter(name=request.resolver_match.app_name).exists():
                # User is logged in, but has insufficient permissions
                raise PermissionDenied
