from django.views.generic import TemplateView, RedirectView, View
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.urls import reverse
from django.utils.module_loading import import_string
from django.views.decorators.clickjacking import xframe_options_exempt
LoginProvider = import_string(settings.LOGIN_PROVIDER_CLASS)


class Frontpage(RedirectView):
    pattern_name = 'indberetning:company-select'


class CreateInberetningCreateView(TemplateView):
    template_name = 'indberetning/create.html'


class CreateIndhandlingsCreateView(TemplateView):
    template_name = 'indberetning/create.html'

    def get_context_data(self, **kwargs):
        ctx = super(CreateIndhandlingsCreateView, self).get_context_data(**kwargs)
        ctx.update({"indberetnings_type": "indhandling"})
        return ctx


class CompanySelect(TemplateView):
    template_name = 'indberetning/company_select.html'


class IndberetningsListView(TemplateView):
    template_name = 'indberetning/list.html'


class SelectIndberetningsType(TemplateView):
    template_name = 'indberetning/type_select.html'


class LoginView(View):
    def get(self, request):
        # Setup the oauth login url and redirect the browser to it.
        provider = LoginProvider.from_settings()
        request.session['login_method'] = provider.name
        return HttpResponseRedirect(provider.login(request))


class LoginCallbackView(View):
    def get(self, request):
        provider = LoginProvider.from_settings()
        if provider.handle_login_callback(request=request):
            # if the call back was successfully, redirect to frontpage
            return HttpResponseRedirect(reverse('indberetning:frontpage'))
        return HttpResponseRedirect(reverse('indberetning:login'))


class LogoutView(View):
    def get(self, request):
        provider = LoginProvider.from_settings()
        return HttpResponseRedirect(provider.logout(request))


class LogoutCallback(View):

    @xframe_options_exempt
    def get(self, request):
        provider = LoginProvider.from_settings()
        provider.handle_logout_callback(request)
        return HttpResponse("")
