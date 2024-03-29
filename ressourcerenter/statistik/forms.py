from django import forms
from django.utils.translation import gettext as _

from administration.models import FiskeArt, Afgiftsperiode
from administration.models import ProduktType
from indberetning.models import IndberetningLinje, Indhandlingssted, Virksomhed
from project.forms_mixin import BootstrapForm


class StatistikForm(BootstrapForm):

    years = forms.MultipleChoiceField(
        label=_('År'),
        choices=(),
        required=True,
    )

    quarter_starting_month = forms.MultipleChoiceField(
        label=_('Kvartal'),
        choices=(
            (1, _('1. kvartal')),
            (4, _('2. kvartal')),
            (7, _('3. kvartal')),
            (10, _('4. kvartal')),
        ),
        required=True,
    )

    virksomhed = forms.ModelMultipleChoiceField(
        label=_('Virksomhed'),
        queryset=Virksomhed.objects.all(),
        required=False,
    )

    fartoej = forms.MultipleChoiceField(
        label=_('Fartøjs navn'),
        choices=(),
        required=False,
    )

    indberetningstype = forms.MultipleChoiceField(
        label=_('Indberetningstype'),
        choices=[(x, x) for x in ('Indhandling', 'Eksport')],
        required=False,
    )

    indhandlingssted = forms.ModelMultipleChoiceField(
        label=_('Indhandlingssted'),
        queryset=Indhandlingssted.objects.all(),
        required=False,
    )

    fiskeart = forms.ModelMultipleChoiceField(
        label=_('Fiskeart'),
        queryset=FiskeArt.objects.all(),
        required=False,
    )

    produkttype = forms.ModelMultipleChoiceField(
        label=_('Produkttype'),
        queryset=ProduktType.objects.filter(gruppe__isnull=False),
        required=False,
    )

    enhed = forms.MultipleChoiceField(
        label=_('Enhed'),
        choices=(
            ('levende_ton', _('Levende vægt tons')),
            ('produkt_ton', _('Produkt vægt tons')),
            ('omsætning_m_transport_tkr', _('Omsætning inkl. transporttillæg, tusinde kr.')),
            ('omsætning_m_bonus_tkr', _('Omsætning inkl. bonus, tusinde kr.')),
            ('omsætning_u_bonus_tkr', _('Omsætning ekskl. bonus, tusinde kr.')),
            ('bonus_tkr', _('Bonus')),
            ('afgift_tkr', _('Beregnet afgiftsbetaling, tusinde kr.')),
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        # Years should be distinct years for known afgiftsperioder
        self.base_fields['years'].choices = [
            (x['dato_fra__year'], str(x['dato_fra__year'])) for x in
            Afgiftsperiode.objects.values(
                'dato_fra__year'
            ).order_by('-dato_fra__year').distinct()
        ]

        # Fartoej should be distinct fartøj names
        self.base_fields['fartoej'].choices = [
            (x['fartøj_navn'], x['fartøj_navn']) for x in
            IndberetningLinje.objects.filter(fartøj_navn__isnull=False).values(
                'fartøj_navn'
            ).order_by('fartøj_navn').distinct()
        ]

        super(StatistikForm, self).__init__(*args, **kwargs)
