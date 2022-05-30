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

    fiskeart_eksport = forms.ModelMultipleChoiceField(
        label=_('Fiskeart (eksport)'),
        queryset=FiskeArt.objects.all(),
        required=False,
    )

    produkttype_eksport = forms.ModelMultipleChoiceField(
        label=_('Produkttype (eksport)'),
        queryset=ProduktType.objects.filter(gruppe__isnull=False),
        required=False,
    )

    fiskeart_indhandling = forms.ModelMultipleChoiceField(
        label=_('Fiskeart (indhandling)'),
        queryset=FiskeArt.objects.all(),
        required=False,
    )

    enhed = forms.MultipleChoiceField(
        label=_('Enhed'),
        choices=(
            ('produkt_ton', _('Produkt vægt tons')),
            ('levende_ton', _('Levende vægt tons')),
            ('omsætning_tkr', _('Omsætning, tusinde kr.')),
            ('transporttillæg_tkr', _('Transporttillæg, tusinde kr.')),
            ('bonus_tkr', _('Bonus, tusinde kr.')),
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
