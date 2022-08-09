from administration.models import FiskeArt, Afgiftsperiode
from administration.models import ProduktType
from django import forms
from django.db.models import Q
from django.utils.translation import gettext as _
from indberetning.models import IndberetningLinje, Indhandlingssted, Virksomhed
from project.forms_mixin import BootstrapForm


class StatistikBaseForm(forms.Form):

    MONTH_JANUAR = "1"
    MONTH_APRIL = "4"
    MONTH_JULI = "7"
    MONTH_OKTOBER = "10"

    # Deaktiveret jf. #51072, men skal aktiveres senere
    # skematype_3 = forms.ChoiceField(
    #     choices=(('0', 'Fra fartøj'), ('1', 'Fra fabrik')),
    #     required=True,
    #     widget=forms.RadioSelect()
    # )

    years = forms.MultipleChoiceField(
        label=_("År"),
        choices=(),
        required=True,
    )

    quarter_starting_month = forms.MultipleChoiceField(
        label=_("Kvartal"),
        choices=(
            (MONTH_JANUAR, _("1. kvartal")),
            (MONTH_APRIL, _("2. kvartal")),
            (MONTH_JULI, _("3. kvartal")),
            (MONTH_OKTOBER, _("4. kvartal")),
        ),
        required=True,
    )

    virksomhed = forms.ModelMultipleChoiceField(
        label=_("Virksomhed"),
        queryset=Virksomhed.objects.all(),
        required=False,
    )

    fartoej = forms.MultipleChoiceField(
        label=_("Fartøjs navn"),
        choices=(),
        required=False,
    )

    indberetningstype = forms.MultipleChoiceField(
        label=_("Indberetningstype"),
        choices=[(x, x) for x in ("Eksport", "Indhandling")],
        required=False,
    )

    fiskeart_eksport = forms.ModelMultipleChoiceField(
        label=_("Fiskeart (eksport)"),
        queryset=FiskeArt.objects.all(),
        required=False,
    )

    produkttype_eksport = forms.ModelMultipleChoiceField(
        label=_("Produkttype (eksport)"),
        queryset=ProduktType.objects.filter(
            Q(gruppe__isnull=False) | Q(fartoej_groenlandsk__isnull=False)
        ),
        required=False,
    )

    fiskeart_indhandling = forms.ModelMultipleChoiceField(
        label=_("Fiskeart (indhandling)"),
        queryset=FiskeArt.objects.all(),
        required=False,
    )

    indhandlingssted = forms.ModelMultipleChoiceField(
        label=_("Indhandlingssted"),
        queryset=Indhandlingssted.objects.all(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        # Years should be distinct years for known afgiftsperioder
        self.base_fields["years"].choices = [
            (x["dato_fra__year"], str(x["dato_fra__year"]))
            for x in Afgiftsperiode.objects.values("dato_fra__year")
            .order_by("-dato_fra__year")
            .distinct()
        ]

        # Fartoej should be distinct fartøj names
        self.base_fields["fartoej"].choices = [
            (x["fartøj_navn"], x["fartøj_navn"])
            for x in IndberetningLinje.objects.filter(fartøj_navn__isnull=False)
            .values("fartøj_navn")
            .order_by("fartøj_navn")
            .distinct()
        ]

        super().__init__(*args, **kwargs)


class StatistikForm(BootstrapForm, StatistikBaseForm):

    enhed = forms.MultipleChoiceField(
        label=_("Enhed"),
        choices=(
            ("produkt_ton", _("Produkt vægt tons")),
            ("levende_ton", _("Levende vægt tons")),
            ("omsætning_tkr", _("Omsætning, tusinde kr.")),
            ("transporttillæg_tkr", _("Transporttillæg, tusinde kr.")),
            ("bonus_tkr", _("Bonus, tusinde kr.")),
            ("afgift_tkr", _("Beregnet afgiftsbetaling, tusinde kr.")),
        ),
        required=True,
    )
