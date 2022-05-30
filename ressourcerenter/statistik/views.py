from administration.models import Afgiftsperiode, FiskeArt
from django.db.models import Case, Value, When
from django.db.models import Sum
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import FormView
from indberetning.models import IndberetningLinje
from project.views_mixin import ExcelMixin
from statistik.forms import StatistikForm


class StatistikView(ExcelMixin, FormView):
    form_class = StatistikForm
    template_name = 'statistik/statistik_form.html'
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
        # Output is a table containing a series of identifier columns with
        # search/grouping criteria and their values. The columns for year
        # and quarter will always be present, other identifier columns depend
        # on the user having picked at least one value for that field.
        # The last columns in the table will always be the selected values;
        # ie. the aggregated Sum of the value specified by the unit column,
        # grouped over the identifying columns.
        annotations = {}

        grouping_fields = {}
        grouping_fields['years'] = 'indberetning__afgiftsperiode__dato_fra__year'
        grouping_fields['quarter_starting_month'] = 'indberetning__afgiftsperiode__dato_fra__month'
        ordering_fields = {}

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
                When(indberetning__skematype__id=1, then=Value('Eksport')),  # Values skal matche form.indberetningstype.choices
                default=Value('Indhandling'),
            ))
            grouping_fields['indberetningstype'] = 'indberetningstype'
            qs = qs.filter(indberetningstype__in=form.cleaned_data['indberetningstype'])

        if form.cleaned_data['fiskeart']:
            grouping_fields['fiskeart'] = 'produkttype__fiskeart__navn_dk'
            qs = qs.filter(produkttype__fiskeart__in=form.cleaned_data['fiskeart'])

        if form.cleaned_data['produkttype']:
            grouping_fields['produkttype'] = 'produkttype__navn_dk'
            ordering_fields['produkttype'] = 'produkttype__ordering'
            qs = qs.filter(produkttype__in=form.cleaned_data['produkttype'])

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
            annotations['omsætning_m_bonus_tkr'] = Sum('bonus')
        if 'bonus_tkr' in enheder:
            annotations['bonus'] = Sum('bonus')
        if 'afgift_tkr' in enheder:
            annotations['afgift_tkr'] = Sum('fangstafgift__afgift')

        headings = [form.fields[x].label for x in grouping_fields.keys()]
        headings += [self.display_enhed(enhed) for enhed in enheder]
        for key, value in grouping_fields.items():
            if key not in ordering_fields:
                ordering_fields[key] = value

        qs = qs.values(*grouping_fields.values()).annotate(**annotations).order_by(
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
