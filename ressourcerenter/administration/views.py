from django import forms
from django.utils.functional import cached_property
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic import CreateView, UpdateView
from django.urls import reverse

from administration.views_mixin import HistoryMixin

from administration.forms import AfgiftsperiodeForm, SatsTabelElementForm, SatsTabelElementFormSet
from administration.models import Afgiftsperiode, Ressource, SatsTabelElement

from administration.forms import FiskeArtForm
from administration.models import FiskeArt

from administration.forms import ProduktKategoriForm
from administration.models import ProduktKategori


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


class AfgiftsperiodeHistoryView(HistoryMixin, DetailView):

    model = Afgiftsperiode

    def get_fields(self, **kwargs):
        return ('navn', 'vis_i_indberetning',)

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

    @cached_property
    def resources(self):
        return Ressource.objects.all().order_by('fiskeart__navn', 'fiskeart__navn')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'form_kwargs': {
                'ressourcer': list(self.resources)
            },
            'queryset': self.object.entries.order_by('ressource__fiskeart__navn', 'ressource__fangsttype__navn'),
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
            'rate_pr_kg_indhandling',
            'rate_pr_kg_export',
            'rate_prkg_groenland',
            'rate_prkg_udenlandsk',
            'rate_procent_indhandling',
            'rate_procent_export',
        )

    def get_back_url(self):
        return reverse('administration:afgiftsperiode-satstabel', kwargs={'pk': self.object.periode.pk})

# endregion


# region FiskeArt

class FiskeArtCreateView(CreateView):

    model = FiskeArt
    form_class = FiskeArtForm

    def get_success_url(self):
        return reverse('administration:fiskeart-list')


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

    def get_back_url(self):
        return reverse('administration:fiskeart-list')

# endregion


# region ProduktKategori

class ProduktKategoriCreateView(CreateView):

    model = ProduktKategori
    form_class = ProduktKategoriForm

    def get_success_url(self):
        return reverse('administration:produktkategori-list')

    def get_context_data(self, **kwargs):
        return super(ProduktKategoriCreateView, self).get_context_data(**{
            **kwargs,
            'creating': True
        })


class ProduktKategoriUpdateView(UpdateView):

    model = ProduktKategori
    form_class = ProduktKategoriForm

    def get_success_url(self):
        return reverse('administration:produktkategori-list')


class ProduktKategoriListView(ListView):

    model = ProduktKategori


class ProduktKategoriHistoryView(HistoryMixin, DetailView):

    model = ProduktKategori

    def get_fields(self, **kwargs):
        return ('navn', 'beskrivelse',)

    def get_back_url(self):
        return reverse('administration:produktkategori-list')
