import mimetypes

from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.utils.functional import cached_property
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView, RedirectView, ListView, FormView, View, DetailView, UpdateView
from django.forms import inlineformset_factory

from administration.models import Afgiftsperiode, SkemaType
from indberetning.forms import IndberetningsTypeSelectForm, VirksomhedsAddressForm, BilagsFormSet
from indberetning.forms import IndberetningsLinjeSkema1Form, IndberetningsLinjeSkema2Form, IndberetningsLinjeSkema3Form
from indberetning.models import Indberetning, Virksomhed, IndberetningLinje, Bilag
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
            'companies': dafo_client.get_owner_information(self.request.session['cpr'])
        })
        # TODO handle when there is no companies
        # Show a warning and logout the user?
        return ctx


class IndberetningsListView(ListView):
    def get_queryset(self):
        return Indberetning.objects.filter(virksomhed__cvr=self.request.session['cvr'])


class SelectIndberetningsType(FormView):
    form_class = IndberetningsTypeSelectForm
    template_name = 'indberetning/type_select.html'

    def form_valid(self, form):
        periode_uuid = form.cleaned_data['periode'].uuid
        skema_id = form.cleaned_data['skema'].id

        return HttpResponseRedirect(reverse('indberetning:indberetning-create', kwargs={'periode': periode_uuid, 'skema': skema_id}))


class IndberetningsLinjebilagFormsetMixin:

    def get_linje_form(self):
        if self.skema.id == 1:
            return IndberetningsLinjeSkema1Form
        if self.skema.id == 2:
            return IndberetningsLinjeSkema2Form
        if self.skema.id == 3:
            return IndberetningsLinjeSkema3Form

    def get_form_class(self):
        formset_class = inlineformset_factory(
            parent_model=Indberetning,
            model=IndberetningLinje,
            form=self.get_linje_form(),
            can_delete=False,
            validate_min=True,
            extra=1
        )
        return formset_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'prefix': 'linje',
            'auto_id': False,
            'form_kwargs': {
                'cvr': self.request.session['cvr']
            }
        })
        if 'data' not in kwargs:
            kwargs['queryset'] = IndberetningLinje.objects.none()
        return kwargs

    def get_context_data(self, **kwargs):
        if 'bilag_formset' not in kwargs:
            kwargs['bilag_formset'] = BilagsFormSet(auto_id=False,
                                                    prefix='bilag',
                                                    queryset=Bilag.objects.none())
        ctx = super(IndberetningsLinjebilagFormsetMixin, self).get_context_data(**kwargs)
        return ctx

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        bilag_formset = BilagsFormSet(request.POST,
                                      request.FILES,
                                      auto_id=False,
                                      prefix='bilag')
        if form.is_valid() and bilag_formset.is_valid():
            return self.form_valid(form, bilag_formset)
        else:
            return self.form_invalid(form, bilag_formset)

    def form_valid(self, formset, bilag_formset):
        print("form_valid")
        indberetning = self.get_indberetning_instance()
        indberetning.save()
        linjer = []
        for line in formset.save(commit=False):
            # need to set FK
            line.indberetning = indberetning
            line.save()
            linjer.append(line)
        bilags = []
        for bilag in bilag_formset.save(commit=False):
            print(bilag)
            bilag.indberetning = indberetning
            bilag.save()
            bilags.append(bilag)

        return linjer, bilags

    def form_invalid(self, formset, bilag_formset):
        return self.render_to_response(self.get_context_data(form=formset, bilag_formset=bilag_formset))


class CreateIndberetningCreateView(IndberetningsLinjebilagFormsetMixin, FormView):
    """
    Creat view for kystnært (fartøj)/pelagisk (havgående) fiskeri og måske flere.
    """
    template_name = 'indberetning/indberetning_form.html'
    indberetnings_type = 'fartøj'

    @cached_property
    def afgiftsperiode(self):
        return Afgiftsperiode.objects.get(uuid=self.kwargs['periode'])

    @cached_property
    def skema(self):
        return SkemaType.objects.get(id=self.kwargs['skema'])

    def get_indberetning_instance(self):
        """
        :return: an unsaved instance of indberetning with th virksomhed and afgiftsperiode etc set
        """
        instance = Indberetning(
            indberetnings_type=self.indberetnings_type,
            virksomhed=Virksomhed.objects.get(cvr=self.request.session['cvr']),
            afgiftsperiode=self.afgiftsperiode,
            skematype=self.skema
        )
        if self.request.user.is_authenticated:
            # if the user is logged in as an administrator set the administrator field.
            instance.administrator = self.request.user
        else:
            # nemid bruger indberetter
            instance.indberetters_cpr = self.request.session['cpr']
        return instance

    def get_context_data(self, **kwargs):
        ctx = super(CreateIndberetningCreateView, self).get_context_data(**kwargs)
        ctx.update({
            'form_url': reverse('indberetning:indberetning-create', kwargs={'periode': self.afgiftsperiode.uuid, 'skema': self.skema.id}),
            'afgiftsperiode': self.afgiftsperiode,
            'skema_id': self.skema.id
        })
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(CreateIndberetningCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, formset, bilag_formset):
        linjer, bilags = super(CreateIndberetningCreateView, self).form_valid(formset, bilag_formset)
        fiskearter = set([str(linje.produkttype) for linje in linjer])
        message = _('Ny Indberetning oprettet for: %s.') % ', '.join(fiskearter)
        if len(bilags) > 0:
            message = _('Ny Indberetning oprettet for: %(fiskearter)s med %(bilag)s bilag.') %\
                {'fiskearter': ', '.join(fiskearter),
                 'bilag': len(bilags)}

        messages.add_message(self.request,
                             messages.INFO,
                             message)
        return redirect(reverse('indberetning:indberetning-list'))


class UpdateIndberetningsView(IndberetningsLinjebilagFormsetMixin, UpdateView):
    template_name = 'indberetning/indberetning_form.html'

    @cached_property
    def skema(self):
        return self.object.skematype

    def get_indberetning_instance(self):
        return self.object

    def get_queryset(self):
        # always limit the QS to indberetninger belonging to the company.
        # check for session['cvr'] is done in middleware,
        # so we can always assume it is set when processing the view
        return Indberetning.objects.filter(
            virksomhed__cvr=self.request.session['cvr']).select_related('afgiftsperiode')

    def get_context_data(self, **kwargs):
        ctx = super(UpdateIndberetningsView, self).get_context_data(**kwargs)
        ctx.update({
            'edit_mode': True,
            'form_url': reverse('indberetning:indberetning-edit', kwargs={'pk': self.get_object().uuid}),
            'afgiftsperiode': self.get_object().afgiftsperiode,
            'skema_id': self.skema.id
        })
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(UpdateIndberetningsView, self).post(request, *args, **kwargs)

    def form_valid(self, formset, bilag_formset):
        linjer, bilags = super(UpdateIndberetningsView, self).form_valid(formset, bilag_formset)
        message = None
        if linjer and bilags:
            message = _('Indberetningen blev justeret og tilføjet %d nye bilag.') % len(bilags)
        elif bilags:
            message = _('Der blev tilføjet %d nye bilag til indberetningen') % len(bilags)
        elif linjer:
            message = _('Indberetningen blev justeret.')

        if message:
            messages.add_message(self.request, messages.INFO, message)
        return redirect(reverse('indberetning:indberetning-list'))


class BilagDownloadView(DetailView):

    def get_queryset(self):
        return Bilag.objects.filter(indberetning__virksomhed__cvr=self.request.session['cvr'])

    def render_to_response(self, context, **response_kwargs):
        bilag = self.get_object()
        file = bilag.bilag
        mime_type, _ = mimetypes.guess_type(file.name)
        response = HttpResponse(file.read(), content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % bilag.filename
        return response


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
