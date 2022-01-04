from django import forms
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic import CreateView, UpdateView
from django.urls import reverse
from django.utils.translation import gettext as _
from datetime import timedelta
import re

from administration.views_mixin import ExcelMixin, HistoryMixin

from administration.forms import AfgiftsperiodeForm, SatsTabelElementForm, SatsTabelElementFormSet
from administration.models import Afgiftsperiode, SatsTabelElement

from administration.forms import FiskeArtForm
from administration.models import FiskeArt

from administration.forms import ProduktTypeForm
from administration.models import ProduktType

from indberetning.models import Indberetning
from administration.forms import IndberetningSearchForm

from indberetning.models import IndberetningLinje
from administration.forms import IndberetningLinjeKommentarForm, IndberetningLinjeKommentarFormSet
from administration.forms import IndberetningAfstemForm


class FrontpageView(TemplateView):
    # TODO can be replaced, just needed a landing page.
    template_name = 'administration/frontpage.html'


# region Afgiftsperiode

class AfgiftsperiodeCreateView(CreateView):

    model = Afgiftsperiode
    form_class = AfgiftsperiodeForm

    def get_success_url(self):
        # Sender direkte videre til satstabellen; vi kan overveje bare at sende til listen
        return reverse('administration:afgiftsperiode-satstabel', kwargs={'pk': self.object.pk})


class AfgiftsperiodeListView(ListView):

    model = Afgiftsperiode
    queryset = Afgiftsperiode.objects.all()


class AfgiftsperiodeUpdateView(UpdateView):
    form_class = AfgiftsperiodeForm
    model = Afgiftsperiode

    def get_success_url(self):
        return reverse('administration:afgiftsperiode-list')


class AfgiftsperiodeHistoryView(HistoryMixin, DetailView):

    model = Afgiftsperiode

    def get_fields(self, **kwargs):
        return ('navn', 'vis_i_indberetning', 'beregningsmodel')

    def get_back_url(self):
        return reverse('administration:afgiftsperiode-list')


class AfgiftsperiodeSatsTabelUpdateView(UpdateView):

    model = Afgiftsperiode
    form_class = forms.inlineformset_factory(
        Afgiftsperiode,
        SatsTabelElement,
        formset=SatsTabelElementFormSet,
        form=SatsTabelElementForm,
        extra=0,
        can_delete=False
    )

    template_name = 'administration/afgiftsperiode_satstabel.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'queryset': self.object.entries.order_by(
                'skematype__navn_dk',
                'fiskeart__navn_dk',
                'fartoej_groenlandsk'
            ),
            'instance': self.object,
        })
        return kwargs

    def get_success_url(self):
        return reverse('administration:afgiftsperiode-list')

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            **kwargs,
            'periode': self.object,
        })


class SatsTabelElementHistoryView(HistoryMixin, DetailView):

    model = SatsTabelElement

    def get_fields(self):
        return (
            'rate_pr_kg',
            'rate_procent',
        )

# endregion


# region FiskeArt

class FiskeArtCreateView(CreateView):

    model = FiskeArt
    form_class = FiskeArtForm

    def get_success_url(self):
        return reverse('administration:fiskeart-list')

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            **kwargs,
            'creating': True
        })


class FiskeArtUpdateView(UpdateView):

    model = FiskeArt
    form_class = FiskeArtForm

    def get_success_url(self):
        return reverse('administration:fiskeart-list')


class FiskeArtListView(ListView):

    model = FiskeArt


class FiskeArtHistoryView(HistoryMixin, DetailView):

    model = FiskeArt

    def get_fields(self, **kwargs):
        return ('navn', 'beskrivelse',)

# endregion


# region ProduktType

class ProduktTypeCreateView(CreateView):

    model = ProduktType
    form_class = ProduktTypeForm

    def get_success_url(self):
        return reverse('administration:produkttype-list')

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            **kwargs,
            'creating': True
        })


class ProduktTypeUpdateView(UpdateView):

    model = ProduktType
    form_class = ProduktTypeForm

    def get_success_url(self):
        return reverse('administration:produkttype-list')


class ProduktTypeListView(ListView):

    model = ProduktType


class ProduktTypeHistoryView(HistoryMixin, DetailView):

    model = ProduktType

    def get_fields(self, **kwargs):
        return ('navn', 'beskrivelse',)


class IndberetningDetailView(UpdateView):
    template_name = 'administration/indberetning_detail.html'
    model = Indberetning

    form_class = forms.inlineformset_factory(
        Indberetning,
        IndberetningLinje,
        form=IndberetningLinjeKommentarForm,
        formset=IndberetningLinjeKommentarFormSet,
        extra=0,
        can_delete=False
    )

    def get_success_url(self):
        # The list may supply its full url in the `back`-parameter,
        # so that we return to the last search results instead of the unfiltered list
        return self.request.GET.get('back', reverse('administration:indberetning-list'))


class IndberetningAfstemFormView(UpdateView):
    model = Indberetning
    form_class = IndberetningAfstemForm

    def get_success_url(self):
        return reverse('administration:indberetning-detail', kwargs={'pk': self.object.pk})


class IndberetningListView(ExcelMixin, ListView):
    template_name = 'administration/indberetning_list.html'  # Eksplicit for at undgå navnekollision med template i indberetning
    model = Indberetning
    form_class = IndberetningSearchForm

    excel_fields = (
        (_('Afgiftsperiode'), 'afgiftsperiode__navn'),
        (_('Virksomhed'), 'virksomhed__cvr'),
        (_('Cpr'), 'indberetters_cpr'),
        (_('Indberetningstidspunkt'), 'indberetningstidspunkt'),
        (_('Navn'), 'navn'),
        (_('Fiskearter'), 'get_fishcategories_string')
    )

    def get_form(self):
        return self.form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        return {
            'data': self.request.GET,
        }

    def get_queryset(self):
        form = self.get_form()
        qs = self.model.objects.all()
        if form.is_valid():
            data = form.cleaned_data
            if data['afgiftsperiode']:
                qs = qs.filter(afgiftsperiode=data['afgiftsperiode'])
            if data['beregningsmodel']:
                qs = qs.filter(afgiftsperiode__beregningsmodel=data['beregningsmodel'])
            if data['tidspunkt_fra']:
                qs = qs.filter(indberetningstidspunkt__gte=data['tidspunkt_fra'])
            if data['tidspunkt_til']:
                qs = qs.filter(indberetningstidspunkt__lt=data['tidspunkt_til'] + timedelta(days=1))
            if data['cvr']:
                qs = qs.filter(virksomhed__cvr__contains=re.sub(r'[^\d]', '', data['cvr']))
            if data['produkttype']:
                qs = qs.filter(linjer__produkttype=data['produkttype'])
        return qs

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            **kwargs,
            'form': self.get_form()
        })
