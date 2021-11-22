from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.module_loading import import_string
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView, RedirectView, ListView, FormView, View, DetailView, UpdateView

from administration.models import Afgiftsperiode
from indberetning.forms import IndberetningsTypeSelectForm, VirksomhedsAddressForm
from indberetning.models import Indberetning, Virksomhed, IndberetningLinje
from project.dafo import DatafordelerClient

LoginProvider = import_string(settings.LOGIN_PROVIDER_CLASS)


class Frontpage(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        cvr = self.request.session.get('cvr')
        if cvr:
            # lookup company information
            dafo_client = DatafordelerClient.from_settings()
            # TODO handle when dafo/pitu is not reachable
            self.request.session['company_information'] = dafo_client.get_company_information(cvr)
            try:
                virksomhed, created = Virksomhed.objects.get_or_create(cvr=cvr)
            except IntegrityError:
                # virksomhed exists so get it
                created = False
                virksomhed = Virksomhed.objects.get(cvr=cvr)
            if created:
                # Hvis cvr nummeret lige er blevet oprettet,
                # redirect til redigering af administrativ adresse.
                return reverse('indberetning:company-edit', kwargs={'pk': virksomhed.uuid})
            return reverse('indberetning:indberetning-list')
        return reverse('indberetning:company-select')


class VirksomhedUpdateView(UpdateView):
    model = Virksomhed
    form_class = VirksomhedsAddressForm

    def get_success_url(self):
        return reverse('indberetning:indberetning-list')


class CompanySelectView(TemplateView):
    template_name = 'indberetning/company_select.html'

    def get_context_data(self, **kwargs):
        ctx = super(CompanySelectView, self).get_context_data(**kwargs)
        dafo_client = DatafordelerClient.from_settings()
        ctx.update({
            'companies': dafo_client.get_owned_companies(self.request.session['cpr'])
        })
        # TODO handle when there is no companies
        # Show a warning and logout the user?
        return ctx


class IndberetningsListView(ListView):
    def get_queryset(self):
        return IndberetningLinje.objects.filter(indberetning__virksomhed__cvr=self.request.session['cvr'])


class SelectIndberetningsType(FormView):
    form_class = IndberetningsTypeSelectForm
    template_name = 'indberetning/type_select.html'

    def form_valid(self, form):
        periode_uuid = form.cleaned_data['periode'].uuid
        if form.cleaned_data['type'] == 'indhandling':
            pass
        return HttpResponseRedirect(reverse('indberetning:indberetning-create', kwargs={'pk': periode_uuid}))


class CreateIndberetningCreateView(DetailView):
    template_name = 'indberetning/indberetning_create.html'
    model = Afgiftsperiode
    # TODO handle form post

    def get_context_data(self, **kwargs):
        ctx = super(CreateIndberetningCreateView, self).get_context_data(**kwargs)
        ctx.update({
            'tidligere_indberetninger': Indberetning.objects.filter(indberetnings_type='havgående',
                                                                    afgiftsperiode=self.get_object(),
                                                                    virksomhed__cvr=self.request.session['cvr'])
        })
        return ctx


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
