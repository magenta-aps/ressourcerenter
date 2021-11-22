from django.contrib.auth.views import redirect_to_login
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.module_loading import import_string


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._administrator_login_url = reverse(settings.LOGIN_URL)
        self._indberetning_login_url = reverse('indberetning:login')
        self._indberetning_callback_url = reverse('indberetning:login-callback')
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
                            self._indberetning_callback_url):
            return None
        if request.resolver_match.app_name == 'administration' and request.user.is_authenticated is False:
            # user not logged in, but trying to access a page from the administration app
            return redirect_to_login(request.get_full_path(), self._administrator_login_url, 'next')
        elif request.resolver_match.app_name == 'indberetning':
            if self._login_provider.user_is_logged_in(request) is False:
                # nemId user not logged in so redirect to login page
                return HttpResponseRedirect(self._indberetning_login_url)
            elif request.session.get('cvr') is None and request.path != reverse('indberetning:company-select'):
                # if the session do not contain a cvr number,
                # always redirect to the company select page
                return HttpResponseRedirect(reverse('indberetning:company-select'))
