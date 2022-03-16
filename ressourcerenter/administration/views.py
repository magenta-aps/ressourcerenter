from django import forms
from django.conf import settings
from django.db.models.query import prefetch_related_objects
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.views.generic import RedirectView
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic import CreateView, UpdateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import BaseFormView
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.functional import cached_property

from django.db.models import F, Sum
from django.db.models import Case, Value, When
from django.db.models.functions import Coalesce
from datetime import timedelta
import re
from decimal import Decimal
from datetime import date
from itertools import chain

from collections import OrderedDict

from administration.views_mixin import HistoryMixin
from project.views_mixin import ExcelMixin, GetFormView

from administration.forms import AfgiftsperiodeForm, SatsTabelElementForm, SatsTabelElementFormSet
from administration.models import Afgiftsperiode, SatsTabelElement

from administration.forms import FiskeArtForm
from administration.models import FiskeArt

from administration.forms import ProduktTypeForm
from administration.models import ProduktType

from administration.forms import StatistikForm

from indberetning.models import Indberetning
from administration.forms import IndberetningSearchForm

from indberetning.models import IndberetningLinje
from administration.forms import IndberetningLinjeKommentarForm, IndberetningLinjeKommentarFormSet
from administration.forms import IndberetningAfstemForm

from indberetning.models import Virksomhed
from administration.forms import VirksomhedForm

from administration.models import Faktura, Prisme10QBatch
from administration.forms import FakturaForm

from administration.forms import BatchSendForm


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
        qs = self.object.entries.order_by(
            'skematype__navn_dk',
            'fiskeart__navn_dk',
            'fartoej_groenlandsk'
        ).select_related('fiskeart')
        kwargs.update({
            'queryset': qs,
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
        can_delete=False,
        extra=0,
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
        (_('Afgiftsperiode'), 'afgiftsperiode__navn_dk'),
        (_('Virksomhed'), 'virksomhed__cvr'),
        (_('Cpr'), 'indberetters_cpr'),
        (_('Indberetningstidspunkt'), 'indberetningstidspunkt'),
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
        for related in ('afgiftsperiode', 'virksomhed', 'linjer__produkttype__fiskeart'):
            prefetch_related_objects(self.object_list, related)
        return super().get_context_data(**{
            **kwargs,
            'form': self.get_form()
        })


class FakturaDetailView(DetailView):
    template_name = 'administration/faktura_detail.html'
    model = Faktura

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            **kwargs,
            'destinations_available': settings.PRISME_PUSH['destinations_available']
        })


class VirksomhedListView(ListView):
    model = Virksomhed
    template_name = 'administration/virksomhed_list.html'


class VirksomhedCreateView(CreateView):
    form_class = VirksomhedForm
    model = Virksomhed
    template_name = 'administration/virksomhed_form.html'

    def get_success_url(self):
        return reverse('administration:produkttype-list')


class VirksomhedUpdateView(UpdateView):
    form_class = VirksomhedForm
    model = Virksomhed
    template_name = 'administration/virksomhed_form.html'

    def get_success_url(self):
        return reverse('administration:virksomhed-list')


class VirksomhedRepræsentantView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse('indberetning:indberetning-list')

    def get(self, request, *args, **kwargs):
        try:
            virksomhed = Virksomhed.objects.get(pk=kwargs['pk'])
        except Virksomhed.DoesNotExist:
            return HttpResponseNotFound
        request.session['cvr'] = virksomhed.cvr
        request.session['impersonating'] = True
        return super().get(request, *args, **kwargs)


class VirksomhedRepræsentantStopView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        for key in ('cvr', 'impersonating'):
            try:
                del self.request.session[key]
            except KeyError:
                pass

        if settings.OPENID.get('mock') == 'cvr':
            self.request.session['cvr'] = '12345678'

        return reverse('administration:virksomhed-list')


class StatistikView(ExcelMixin, GetFormView):
    form_class = StatistikForm
    template_name = 'administration/statistik_form.html'
    filename_base = 'statistik'

    def display_kvartal(self, value):
        return {
            '1': _('1. kvartal'),
            '4': _('2. kvartal'),
            '7': _('3. kvartal'),
            '10': _('4. kvartal'),
        }.get(str(value))

    def display_year(self, value):
        return str(value)

    def display_enhed(self, value):
        for x in StatistikForm.base_fields['enhed'].choices:
            if x[0] == value:
                return x[1]

    def get_resultat(self, form):
        # Output is a table containing a series of identifier colums with
        # search/grouping criteria and their values. The columns for year
        # and quarter will always be present, other identifier columns depend
        # on the user having picked at least one value for that field.
        # The last two columns in the table will always be enhed/unit and
        # værdi/value. The value column will contain the aggregated Sum of the
        # value specified by the unit column, grouped over the identifying columns.
        # Identifying columns will only output their value if it has changed from
        # the previous row or if the column to the left of it has output a value.
        annotations = {}

        grouping_fields = OrderedDict()
        grouping_fields['years'] = 'indberetning__afgiftsperiode__dato_fra__year'
        grouping_fields['quarter_starting_month'] = 'indberetning__afgiftsperiode__dato_fra__month'

        # Since year and quarter fields are required we can always filter on them
        perioder = Afgiftsperiode.objects.filter(
            dato_fra__year__in=form.cleaned_data['years'],
            dato_fra__month__in=form.cleaned_data['quarter_starting_month'],
        )

        qs = IndberetningLinje.objects.filter(
            indberetning__afgiftsperiode__in=perioder
        )

        if form.cleaned_data['virksomhed']:
            grouping_fields['virksomhed'] = 'indberetning__virksomhed__cvr'
            qs = qs.filter(indberetning__virksomhed__in=form.cleaned_data['virksomhed'])

        if form.cleaned_data['fartoej']:
            grouping_fields['fartoej'] = 'fartøj_navn'
            qs = qs.filter(fartøj_navn__in=form.cleaned_data['fartoej'])

        if form.cleaned_data['indhandlingssted']:
            grouping_fields['indhandlingssted'] = 'indhandlingssted__navn'
            qs = qs.filter(indhandlingssted__in=form.cleaned_data['indhandlingssted'])

        if form.cleaned_data['indberetningstype']:
            qs = qs.annotate(indberetningstype=Case(
                When(indberetning__skematype__id=2, then=Value('Indhandling')),  # Values skal matche form.indberetningstype.choices
                default=Value('Eksport'),
            ))
            grouping_fields['indberetningstype'] = 'indberetningstype'
            qs = qs.filter(indberetningstype__in=form.cleaned_data['indberetningstype'])

        if form.cleaned_data['fiskeart']:
            grouping_fields['fiskeart'] = 'produkttype__fiskeart__navn_dk'
            qs = qs.filter(produkttype__fiskeart__in=form.cleaned_data['fiskeart'])

        if form.cleaned_data['produkttype']:
            grouping_fields['produkttype'] = 'produkttype__navn_dk'
            qs = qs.filter(produkttype__in=form.cleaned_data['produkttype'])

        qs = qs.select_related('produkttype', 'indberetning', 'indhandlingssted')

        enheder = form.cleaned_data['enhed']
        if 'levende_ton' in enheder:
            annotations['levende_ton'] = Sum('levende_vægt')
        if 'produkt_ton' in enheder:
            annotations['produkt_ton'] = Sum('produktvægt')
        if 'omsætning_m_transport_tkr' in enheder:
            annotations['omsætning_m_transport_tkr'] = Sum(
                Coalesce(F('salgspris'), Decimal('0.0')) + Coalesce(F('transporttillæg'), Decimal('0.0'))
            )
        if 'omsætning_m_bonus_tkr' in enheder:
            annotations['omsætning_m_bonus_tkr'] = Sum(
                Coalesce(F('salgspris'), Decimal('0.0')) + Coalesce(F('bonus'), Decimal('0.0'))
            )
        if 'omsætning_u_bonus_tkr' in enheder:
            annotations['omsætning_u_bonus_tkr'] = Sum('salgspris')
        if 'bonus_tkr' in enheder:
            annotations['bonus'] = Sum('bonus')
        if 'afgift_tkr' in enheder:
            annotations['afgift_tkr'] = Sum('fangstafgift__afgift')

        headings = [form.fields[x].label for x in grouping_fields.keys()]
        headings.append(form.fields['enhed'].label)
        headings.append(_('Værdi'))

        qs = qs.values(*grouping_fields.values()).annotate(**annotations).order_by(
            *grouping_fields.values()
        )

        # Translators for transforming database values to human readable output
        translators = {
            'indberetning__afgiftsperiode__dato_fra__year': self.display_year,
            'indberetning__afgiftsperiode__dato_fra__month': self.display_kvartal
        }

        last_row = [''] * len(grouping_fields)

        # Identifier value for "enhed" field
        last_row.append('')

        number_of_identifiers = len(last_row)

        result = []

        for db_row_dict in qs:
            new_rows = []

            # Add values from grouping fields
            new_row_identifiers = []
            for key in grouping_fields.values():
                value = db_row_dict.get(key)

                if key in translators:
                    value = translators[key](value)

                new_row_identifiers.append(value)

            # Add value for selected enhed and the sum for that enhed/unit
            for enhed in form.cleaned_data['enhed']:
                value = db_row_dict.get(enhed) or 0
                unit_and_value = [
                    self.display_enhed(enhed),
                    value/1000
                ]
                new_rows.append(new_row_identifiers + unit_and_value)

            for new_row in new_rows:
                output_rest_of_identifiers = False
                output_values = []
                # Set values to empty string if they are the same
                # as in the previous row
                for index in range(number_of_identifiers):
                    value = new_row[index]
                    if output_rest_of_identifiers or value != last_row[index]:
                        output_values.append(value)
                        output_rest_of_identifiers = True
                    else:
                        output_values.append('')

                # Append the last column, containing the value
                output_values.append(new_row[number_of_identifiers])

                result.append(output_values)
                last_row = new_row

        return {
            'headings': headings,
            'rows': result
        }

    def headers(self, form):
        return self.get_resultat(form)['headings']

    def rows(self, form):
        return self.get_resultat(form)['rows']

    @cached_property
    def produkt_fiskeart_map(self):
        return {
            str(fiskeart.uuid): [str(produkttype.uuid) for produkttype in fiskeart.produkttype_set.all()]
            for fiskeart in FiskeArt.objects.all()
        }

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            **kwargs,
            'produkt_fiskeart_map': self.produkt_fiskeart_map
        })

    def form_valid(self, form, *args, **kwargs):
        context = self.get_context_data(form=form)
        context.update({
            'form_is_valid': True,
            'resultat': self.get_resultat(form),
            'form': form
        })
        return self.render_to_response(context)


class FakturaCreateView(CreateView):
    form_class = FakturaForm
    model = Faktura
    template_name = 'administration/faktura_form.html'

    def get_success_url(self):
        return reverse('administration:indberetningslinje-list')

    def get_context_data(self, **kwargs):
        destinations_available = settings.PRISME_PUSH['destinations_available']
        return super().get_context_data(
            **{
                **kwargs,
                # Option to send to test is only avaliable when both are possible
                'send_to_test_available': destinations_available['10q_production'] and destinations_available['10q_development']
            }
        )

    def form_valid(self, form):
        linje = get_object_or_404(IndberetningLinje, pk=self.kwargs['pk'])
        batch = Prisme10QBatch.objects.create(oprettet_af=self.request.user)
        faktura = form.save(commit=False)
        faktura.kode = linje.debitorgruppekode
        faktura.periode = linje.indberetning.afgiftsperiode
        faktura.opretter = self.request.user
        faktura.virksomhed = linje.indberetning.virksomhed
        faktura.batch = batch
        faktura.beløb = linje.afgift
        faktura.save()
        linje.faktura = faktura
        linje.save(update_fields=('faktura',))

        destinations_available = settings.PRISME_PUSH['destinations_available']
        # Send to prod if it is available, fall back to dev
        destination = '10q_production'\
            if destinations_available['10q_production'] and not form.cleaned_data['send_to_test']\
            else '10q_development'

        try:
            batch.send(destination, self.request.user)
            messages.add_message(self.request, messages.INFO, _('Faktura oprettet og afsendt'))
        except Exception as e:
            # Exception message has been saved to batch.fejlbesked
            messages.add_message(
                self.request,
                messages.INFO,
                _('Faktura oprettet, men afsendelse fejlede: {error}').format(error=str(e))
            )

        return super().form_valid(form)


class FakturaSendView(SingleObjectMixin, BaseFormView):

    form_class = BatchSendForm
    model = Faktura

    def form_valid(self, form):
        try:
            self.get_object().batch.send(form.cleaned_data['destination'], self.request.user)
            messages.add_message(self.request, messages.INFO, _('Faktura afsendt'))
        except Exception as e:
            # Exception message has been saved to batch.fejlbesked
            messages.add_message(self.request, messages.INFO, _('Afsendelse fejlede: {error}').format(error=str(e)))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.INFO,
            _('Afsendelse fejlede: {error}').format(error=', '.join(chain(*form.errors.values())))
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('administration:faktura-detail', kwargs={'pk': self.get_object().pk})


class IndberetningsLinjeListView(TemplateView):
    template_name = 'administration/indberetning_afstem.html'

    @cached_property
    def periode(self):
        periode_id = self.request.GET.get('periode')
        if periode_id:
            try:
                return Afgiftsperiode.objects.get(pk=periode_id)
            except Afgiftsperiode.DoesNotExist:
                pass
        return Afgiftsperiode.objects.first()

    @cached_property
    def data(self):
        # Opret et træ som grupperer indberetningslinjer i:
        # * Virksomheder
        # * Produkttyper
        # * Fangsttyper
        virksomheder = []
        sum_fields = {'produktvægt', 'levende_vægt', 'salgspris', 'afgift'}

        virksomheder_uuids = [
            virksomhed['virksomhed']
            for virksomhed in Indberetning.objects.filter(afgiftsperiode=self.periode).values('virksomhed').distinct()
        ]
        for virksomhed in Virksomhed.objects.filter(uuid__in=virksomheder_uuids).prefetch_related('indberetning_set'):

            virksomhed_data = {'virksomhed': virksomhed, 'produkttyper': {}}
            virksomheder.append(virksomhed_data)
            for indberetning in virksomhed.indberetning_set.filter(afgiftsperiode=self.periode):
                for linje in indberetning.linjer.all().select_related('faktura', 'produkttype'):

                    produkttype = linje.produkttype
                    if produkttype.uuid not in virksomhed_data['produkttyper']:
                        virksomhed_data['produkttyper'][produkttype.uuid] = {
                            'produkttype': produkttype,
                            'fangsttyper': {}
                        }
                    produkttype_item = virksomhed_data['produkttyper'][produkttype.uuid]

                    fangsttype = linje.fangsttype
                    if fangsttype not in produkttype_item['fangsttyper']:
                        produkttype_item['fangsttyper'][fangsttype] = {
                            'sum': {key: 0 for key in sum_fields},
                            'linjer': []
                        }
                    fangsttype_item = produkttype_item['fangsttyper'][fangsttype]

                    for key in sum_fields:
                        fangsttype_item['sum'][key] += getattr(linje, key)
                    fangsttype_item['linjer'].append(linje)
        return virksomheder

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            **kwargs,
            'data': self.data,
            'afgiftsperioder': Afgiftsperiode.objects.all(),
            'periode': self.periode
        })
