import json
from administration.models import Afgiftsperiode, FiskeArt
from django.db.models import Case, Value, When
from django.db.models import Q
from django.db.models import Sum
from django.db.models import TextField
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import FormView
from indberetning.models import IndberetningLinje
from project.views_mixin import ExcelMixin
from statistik.forms import StatistikBaseForm
from statistik.forms import StatistikForm


class StatistikBaseView(FormView):
    form_class = StatistikForm

    def get_queryset(self, form, only_fields=None):
        grouping_fields = {}
        grouping_fields['years'] = 'indberetning__afgiftsperiode__dato_fra__year'
        grouping_fields['quarter_starting_month'] = 'indberetning__afgiftsperiode__dato_fra__month'
        ordering_fields = {}

        cleaned_data = form.cleaned_data.copy()
        if only_fields is not None:
            for field in cleaned_data:
                if field not in only_fields:
                    cleaned_data[field] = None

        # Since year and quarter fields are required we can always filter on them
        perioder = Afgiftsperiode.objects.filter(
            dato_fra__year__in=cleaned_data['years'],
            dato_fra__month__in=cleaned_data['quarter_starting_month'],
        )

        skematyper = [3] if cleaned_data.get('skematype_3') == '1' else [1, 2]

        qs = IndberetningLinje.objects.filter(
            indberetning__afgiftsperiode__in=perioder,
            indberetning__skematype_id__in=skematyper
        )

        if cleaned_data['virksomhed']:
            grouping_fields['virksomhed'] = 'indberetning__virksomhed__cvr'
            qs = qs.filter(indberetning__virksomhed__in=cleaned_data['virksomhed'])

        if cleaned_data['fartoej']:
            grouping_fields['fartoej'] = 'fartøj_navn'
            qs = qs.filter(fartøj_navn__in=cleaned_data['fartoej'])

        qs = qs.annotate(indberetningstype=Case(
            When(indberetning__skematype__id=1, then=Value('Eksport')),  # Values skal matche form.indberetningstype.choices
            default=Value('Indhandling'),
        ))

        if cleaned_data['indhandlingssted']:
            grouping_fields['indhandlingssted'] = 'indhandlingssted__navn'
            qs = qs.filter(Q(indhandlingssted__in=cleaned_data['indhandlingssted']) | ~Q(indberetningstype='Indhandling'))

        if cleaned_data['indberetningstype']:
            grouping_fields['indberetningstype'] = 'indberetningstype'
            qs = qs.filter(indberetningstype__in=cleaned_data['indberetningstype'])

        if cleaned_data['fiskeart_eksport'] or cleaned_data['fiskeart_indhandling']:
            fiskeart_export_q = Q(indberetning__skematype__id=1)  # eksport
            if cleaned_data['fiskeart_eksport']:
                qs = qs.annotate(fiskeart_eksport=Case(
                    When(indberetning__skematype__id=1, then='produkttype__fiskeart__navn_dk'),  # output-værdi under kolonnen 'fiskeart_eksport'
                    default=Value(''),
                    output_field=TextField(),
                ))
                grouping_fields['fiskeart_eksport'] = 'fiskeart_eksport'  # værdi passer med key i annotate-kaldet
                fiskeart_export_q &= Q(produkttype__fiskeart__in=cleaned_data['fiskeart_eksport'])  # AND valgt produkttype

            fiskeart_indhandling_q = ~Q(indberetning__skematype__id=1)  # not export
            if cleaned_data['fiskeart_indhandling']:
                qs = qs.annotate(fiskeart_indhandling=Case(
                    When(~Q(indberetning__skematype__id=1), then='produkttype__fiskeart__navn_dk'),  # output-værdi under kolonnen 'fiskeart_indhandling'
                    default=Value(''),
                    output_field=TextField(),
                ))
                grouping_fields['fiskeart_indhandling'] = 'fiskeart_indhandling'  # værdi passer med key i annotate-kaldet
                fiskeart_indhandling_q &= Q(produkttype__fiskeart__in=cleaned_data['fiskeart_indhandling'])  # AND valgt produkttype

            qs = qs.filter(fiskeart_export_q | fiskeart_indhandling_q)  # match export query OR indhandling query

        if cleaned_data['produkttype_eksport']:
            ordering_fields['produkttype'] = 'produkttype__ordering'
            qs = qs.annotate(produkttype_eksport=Case(
                When(indberetning__skematype__id=1, then='produkttype__navn_dk'),
                default=Value(''),
                output_field=TextField(),
            ))
            grouping_fields['produkttype_eksport'] = 'produkttype_eksport'
            qs = qs.filter(
                Q(produkttype__in=cleaned_data['produkttype_eksport']) | ~Q(indberetning__skematype__id=1)  # match produkttype OR not export
            )
        return qs, grouping_fields, ordering_fields


class StatistikView(ExcelMixin, StatistikBaseView):
    template_name = 'statistik/statistik_form.html'
    filename_base = 'statistik'

    def display_kvartal(self, value):
        return {
            StatistikBaseForm.MONTH_JANUAR: _('1. kvartal'),
            StatistikBaseForm.MONTH_APRIL: _('2. kvartal'),
            StatistikBaseForm.MONTH_JULI: _('3. kvartal'),
            StatistikBaseForm.MONTH_OKTOBER: _('4. kvartal'),
        }.get(str(value))

    def display_year(self, value):
        return str(value)

    def display_enhed(self, value):
        for x in StatistikForm.base_fields['enhed'].choices:
            if x[0] == value:
                return x[1]

    def get_resultat(self, form):
        # Output is a table containing a series of identifier columns with
        # search/grouping criteria and their values. The columns for year
        # and quarter will always be present, other identifier columns depend
        # on the user having picked at least one value for that field.
        # The last columns in the table will always be the selected values;
        # ie. the aggregated Sum of the value specified by the unit column,
        # grouped over the identifying columns.

        qs, grouping_fields, ordering_fields = self.get_queryset(form)
        annotations = {}
        qs = qs.select_related('produkttype', 'indberetning', 'indhandlingssted')

        enheder = form.cleaned_data['enhed']
        if 'levende_ton' in enheder:
            annotations['levende_ton'] = Sum('levende_vægt')
        if 'produkt_ton' in enheder:
            annotations['produkt_ton'] = Sum('produktvægt')
        if 'omsætning_tkr' in enheder:
            annotations['omsætning_tkr'] = Sum('salgspris')
        if 'transporttillæg_tkr' in enheder:
            annotations['transporttillæg_tkr'] = Sum('transporttillæg')
        if 'bonus_tkr' in enheder:
            annotations['bonus'] = Sum('bonus')
        if 'afgift_tkr' in enheder:
            annotations['afgift_tkr'] = Sum('fangstafgift__afgift')

        headings = [form.fields[x].label for x in grouping_fields.keys()]
        headings += [self.display_enhed(enhed) for enhed in enheder]
        for key, value in grouping_fields.items():
            if key not in ordering_fields:
                ordering_fields[key] = value

        qs = qs.values(
            *grouping_fields.values()
        ).annotate(
            **annotations
        ).order_by(
            *ordering_fields.values()
        )

        # Translators for transforming database values to human readable output
        translators = {
            'indberetning__afgiftsperiode__dato_fra__year': self.display_year,
            'indberetning__afgiftsperiode__dato_fra__month': self.display_kvartal
        }

        result = []

        for db_row_dict in qs:

            # Add values from grouping fields
            new_row_identifiers = []
            for key in grouping_fields.values():
                value = db_row_dict.get(key)
                if key in translators:
                    value = translators[key](value)
                new_row_identifiers.append(value)

            row = new_row_identifiers
            # Add value for selected enhed and the sum for that enhed/unit
            for enhed in enheder:
                value = db_row_dict.get(enhed) or 0
                row.append(value/1000)

            result.append(row)

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


class StatistikChoicesView(StatistikBaseView):

    form_class = StatistikBaseForm

    def form_invalid(self, form):
        return HttpResponseBadRequest(json.dumps(dict(form.errors)))

    def get_data(self, form, field, fields, filter=None):
        qs, grouping_fields, ordering_fields = self.get_queryset(form, fields)
        if filter is not None:
            qs = qs.filter(filter)
        qs = qs.order_by()
        qs = qs.values_list(field, flat=True).distinct()
        return [
            str(value) if value is not None else None
            for value in qs
        ]

    def form_valid(self, form):
        data = {}
        eksport = Q(indberetning__skematype__id=1)
        indhandling = ~eksport
        considered_fields = ['years', 'quarter_starting_month', 'skematype_3']
        # Eksport er valgt hvis form.cleaned_data['indberetningstype'] == ['Eksport'] eller == []
        indberetningstype = form.cleaned_data['indberetningstype']
        is_not_indhandling = len(indberetningstype) > 0 and "Indhandling" not in indberetningstype
        is_not_eksport = len(indberetningstype) > 0 and "Eksport" not in indberetningstype

        # Opdatér et givet felt ud fra felterne ovenover (considered_fields), hvis feltet ikke er sat i formularen
        # Hvis feltet derimod er sat, skal der ikke indskrænkes på det, men feltet skal stadig komme i betragtning længere nede

        considered_fields.append('virksomhed')
        if not form.cleaned_data['virksomhed']:
            data['virksomhed'] = self.get_data(form, 'indberetning__virksomhed', considered_fields)

        considered_fields.append('fartoej')
        if not form.cleaned_data['fartoej']:
            data['fartoej'] = self.get_data(form, 'fartøj_navn', considered_fields)

        considered_fields.append('indberetningstype')
        if not form.cleaned_data['indberetningstype']:
            data['indberetningstype'] = self.get_data(form, 'indberetningstype', considered_fields)

        considered_fields.append('fiskeart_indhandling')
        if is_not_indhandling:
            data['fiskeart_indhandling'] = []
        elif not form.cleaned_data['fiskeart_indhandling']:
            data['fiskeart_indhandling'] = self.get_data(form, 'produkttype__fiskeart__uuid', considered_fields, indhandling)

        considered_fields.append('fiskeart_eksport')
        if is_not_eksport:
            data['fiskeart_eksport'] = []
        elif not form.cleaned_data['fiskeart_eksport']:
            data['fiskeart_eksport'] = self.get_data(form, 'produkttype__fiskeart__uuid', considered_fields, eksport)

        if is_not_eksport:
            data['produkttype_eksport'] = []
        else:
            # Opdatér altid produkttype_eksport, men uden at form-værdien for feltet kommer i betragtning
            # På denne måde bliver data['produkttype_eksport'] kun indskrænket af de andre felter,
            # ikke af feltet selv, også selvom det er sat
            data['produkttype_eksport'] = self.get_data(form, 'produkttype__uuid', considered_fields, eksport)

        considered_fields.append('indhandlingssted')
        if is_not_indhandling:
            # Indskrænk fuldstændigt hvis indhandling ikke er valgt
            data['indhandlingssted'] = []
        elif not form.cleaned_data['indhandlingssted']:
            # Indskrænk hvis indhandlingssted ikke allerede er sat
            data['indhandlingssted'] = self.get_data(form, 'indhandlingssted__uuid', considered_fields)

        all_fiskearter = set(list(form.cleaned_data['fiskeart_eksport']) + list(form.cleaned_data['fiskeart_indhandling']))
        all_value_choices = [value for value, label in StatistikForm().fields['enhed'].choices]
        pelagisk_exception = {'omsætning_tkr', 'transporttillæg_tkr'}  # Disse felter skal skjules hvis der kun er valgt pelagiske fiskearter
        if len(all_fiskearter) > 0:
            if all([fiskeart.pelagisk for fiskeart in all_fiskearter]):
                # Alle valgte fiskearter er pelagiske
                data['enhed'] = list(set(all_value_choices) - pelagisk_exception)
            else:
                data['enhed'] = all_value_choices

        return HttpResponse(json.dumps(data))
