from collections import OrderedDict
from decimal import Decimal
from django.db.models import Case, Value, When
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from administration.models import Afgiftsperiode, FiskeArt
from indberetning.models import IndberetningLinje
from project.views_mixin import ExcelMixin, GetFormView
from statistik.forms import StatistikForm


class StatistikView(ExcelMixin, GetFormView):
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
