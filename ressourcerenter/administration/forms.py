from django import forms
from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from administration.models import Afgiftsperiode, SatsTabelElement, BeregningsModel
from administration.models import FiskeArt
from administration.models import SkemaType
from administration.models import ProduktType
from administration.models import Faktura
from project.forms_mixin import BootstrapForm
from project.form_fields import DateInput
from indberetning.models import Indberetning, Indhandlingssted
from indberetning.models import IndberetningLinje
from indberetning.models import Virksomhed


class AfgiftsperiodeForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = Afgiftsperiode
        fields = ('dato_fra', 'dato_til', 'navn_dk', 'navn_gl', 'beregningsmodel')

        widgets = {
            'navn_dk': forms.widgets.TextInput(),
            'navn_gl': forms.widgets.TextInput(),
        }

    dato_fra = forms.DateField(
        widget=DateInput(format='%Y-%m-%d'),
        input_formats=('%Y-%m-%d',)
    )
    dato_til = forms.DateField(
        widget=DateInput(format='%Y-%m-%d'),
        input_formats=('%Y-%m-%d',)
    )


class FiskeArtForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = FiskeArt
        fields = ('navn_dk', 'navn_gl', 'beskrivelse',)

        widgets = {
            'navn_dk': forms.TextInput(),
            'navn_gl': forms.TextInput(),
            'beskrivelse': forms.TextInput(),
        }


class ProduktTypeForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = ProduktType
        fields = ('navn_dk', 'navn_gl', 'beskrivelse', 'fiskeart', 'fartoej_groenlandsk')

        widgets = {
            'navn_dk': forms.TextInput(),
            'navn_gl': forms.TextInput(),
            'beskrivelse': forms.TextInput(),
            'fartoej_groenlandsk': forms.CheckboxInput(),
        }


class SatsTabelElementFormSet(forms.BaseInlineFormSet):

    def __init__(self, initial=None, min_num=None, **kwargs):
        super(SatsTabelElementFormSet, self).__init__(initial=initial, **kwargs)
        if min_num is not None:
            self.min_num = min_num

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        return kwargs

    @cached_property
    def forms_by_skematype(self):
        by_skematype = {}
        for skematype in SkemaType.objects.all():
            by_skematype[skematype.id] = {'forms': [], 'skematype': skematype}
        for form in self.forms:
            form_skematype_id = form.instance.skematype_id if form.instance else form.data.get('skematype')
            if form_skematype_id and form_skematype_id in by_skematype:
                by_skematype[form_skematype_id]['forms'].append(form)
        return by_skematype.values()


class SatsTabelElementForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = SatsTabelElement
        fields = (
            'periode', 'skematype', 'fiskeart', 'rate_pr_kg', 'rate_procent', 'fartoej_groenlandsk'
        )
        widgets = {
            'skematype': forms.HiddenInput(),
            'fiskeart': forms.HiddenInput(),
            'rate_pr_kg': forms.NumberInput(),
            'rate_procent': forms.NumberInput(),
            'fartoej_groenlandsk': forms.HiddenInput(),
        }


class IndberetningSearchForm(BootstrapForm):
    afgiftsperiode = forms.ModelChoiceField(
        Afgiftsperiode.objects,
        required=False
    )
    beregningsmodel = forms.ModelChoiceField(
        BeregningsModel.objects,
        required=False
    )
    tidspunkt_fra = forms.DateField(
        required=False,
        widget=DateInput()
    )
    tidspunkt_til = forms.DateField(
        required=False,
        widget=DateInput()
    )
    cvr = forms.CharField(
        required=False
    )
    produkttype = forms.ModelChoiceField(
        ProduktType.objects,
        required=False
    )


class IndberetningAfstemForm(forms.ModelForm):
    class Meta:
        model = Indberetning
        fields = ('afstemt',)


class IndberetningLinjeKommentarForm(forms.ModelForm, BootstrapForm):
    class Meta:
        model = IndberetningLinje
        fields = ('kommentar',)
        widgets = {
            'kommentar': forms.Textarea(attrs={'class': 'single-line'})
        }


class IndberetningLinjeKommentarFormSet(forms.BaseInlineFormSet):

    @cached_property
    def forms_by_produkttype(self):
        by_produkttype = {}
        for produkttype in ProduktType.objects.all():
            by_produkttype[produkttype.uuid] = {'forms': [], 'produkttype': produkttype, 'instances': [], 'afgift_sum': 0}
        for form in self.forms:
            form_produkttype = form.instance.produkttype if form.instance else form.data.get('produkttype')
            if form_produkttype:
                group = by_produkttype[form_produkttype.uuid]
                group['forms'].append(form)
                group['instances'].append(form.instance)
        return by_produkttype.values()


class VirksomhedForm(forms.ModelForm, BootstrapForm):
    class Meta:
        model = Virksomhed
        fields = ('cvr', 'kontakt_person', 'kontakt_email', 'kontakts_phone_nr')
        widgets = {
            'cvr': forms.TextInput(),
            'kontakt_person': forms.TextInput(),
            'kontakt_email': forms.TextInput(),
            'kontakts_phone_nr': forms.TextInput(),
        }


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


class FakturaForm(BootstrapForm, forms.ModelForm):

    class Meta:
        model = Faktura
        fields = ('betalingsdato',)
        widgets = {
            'betalingsdato': DateInput()
        }

    send_to_test = forms.BooleanField(
        required=False
    )


class BatchSendForm(forms.Form):

    destination = forms.ChoiceField(
        choices=[(key, key) for key, value in settings.PRISME_PUSH['destinations_available'].items() if value]
    )
