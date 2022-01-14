from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, CharField, ModelForm, modelformset_factory, Select, Textarea
from django.utils import timezone
from django.utils.translation import gettext as _


from administration.models import Afgiftsperiode, ProduktType, SkemaType
from indberetning.models import Bilag, Virksomhed, IndberetningLinje, Navne, Indberetning
from project.form_fields import LocalizedDecimalField
from project.forms_mixin import BootstrapForm


class VirksomhedsAddressForm(ModelForm):
    kontakt_person = CharField(required=False)
    kontakt_email = CharField(required=False)
    kontakts_phone_nr = CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(VirksomhedsAddressForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Virksomhed
        fields = ('kontakt_person', 'kontakt_email', 'kontakts_phone_nr')


class IndberetningsTypeSelectForm(BootstrapForm):
    skema = ModelChoiceField(queryset=SkemaType.objects.all(), required=True)
    periode = ModelChoiceField(queryset=Afgiftsperiode.objects.filter(vis_i_indberetning=True),
                               required=True, empty_label=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default to the period for todays date
        today = timezone.now().date()
        current_periode = Afgiftsperiode.objects.filter(dato_fra__lte=today, dato_til__gt=today).first()
        if current_periode:
            self.fields['periode'].initial = current_periode.uuid


class IndberetningsLinjeBeregningForm(ModelForm):
    """
    Basisform til on-the-fly beregninger
    """
    class Meta:
        model = IndberetningLinje
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris')

    salgsvægt = LocalizedDecimalField()
    levende_vægt = LocalizedDecimalField()
    salgspris = LocalizedDecimalField(required=False)
    pelagisk_nonrequired_fields = ()

    def clean(self):
        cleaned_data = super().clean()
        if ('salgsvægt' in cleaned_data or 'levende_vægt' in cleaned_data) and 'salgspris' in cleaned_data:
            numbers = filter(None, (cleaned_data.get('salgsvægt'), cleaned_data.get('levende_vægt'), cleaned_data['salgspris']))
            if not (all(i > 0 for i in numbers) or all(i < 0 for i in numbers)):
                raise ValidationError(_('Salgsvægt, levende vægt og salgspris skal alle være negative eller positive tal'))
        return cleaned_data


class IndberetningsLinjeForm(BootstrapForm, IndberetningsLinjeBeregningForm):
    """
    Basisform til indberetningslinjer
    """
    def __init__(self, *args, **kwargs):
        self.cvr = kwargs.pop('cvr')
        super().__init__(*args, **kwargs)
        if 'fartøj_navn' in self.fields:
            self.fields['fartøj_navn'].widget.choices = [(n.navn, n.navn) for n in Navne.objects.filter(virksomhed__cvr=self.cvr, type='fartøj')]
        if 'indhandlingssted' in self.fields:
            self.fields['indhandlingssted'].widget.choices = [(n.navn, n.navn) for n in Navne.objects.filter(virksomhed__cvr=self.cvr, type='indhandlings_sted')]

    class Meta:
        model = IndberetningLinje
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris', 'fartøj_navn', 'indhandlingssted', 'kommentar')


class IndberetningsLinjeSkema1Form(IndberetningsLinjeForm):
    produkttype = ModelChoiceField(queryset=ProduktType.objects.filter(fiskeart__skematype=1).order_by('fiskeart__pelagisk', 'navn_dk'), required=True)
    transporttillæg = LocalizedDecimalField(initial=0)
    fartøj_navn = CharField(widget=Select(attrs={'class': "js-boat-select form-control col-2 ", 'autocomplete': "off", 'style': 'width:100%'}))
    kommentar = CharField(widget=Textarea(attrs={'class': 'single-line form-control'}), required=False)

    def clean(self):
        cleaned_data = super().clean()
        produkttype = cleaned_data.get('produkttype')
        if produkttype and not cleaned_data['produkttype'].fiskeart.pelagisk:
            for field in ('salgspris',):
                if cleaned_data.get(field) is None:
                    raise ValidationError({field: self.fields[field].error_messages['required']}, code='required')
        return cleaned_data

    class Meta:
        model = IndberetningLinje
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris', 'fartøj_navn', 'transporttillæg', 'kommentar')


class IndberetningsLinjeSkema2Form(IndberetningsLinjeForm):
    produkttype = ModelChoiceField(queryset=ProduktType.objects.filter(fiskeart__skematype=2).order_by('fiskeart__pelagisk', 'navn_dk'), required=True)
    bonus = LocalizedDecimalField(initial=0)
    fartøj_navn = CharField(widget=Select(attrs={'class': "js-boat-select form-control col-2 ", 'autocomplete': "off", 'style': 'width:100%'}))
    indhandlingssted = CharField(widget=Select(attrs={'class': "js-place-select form-control col-2 ", 'autocomplete': "off", 'style': 'width:100%'}))
    kommentar = CharField(widget=Textarea(attrs={'class': 'single-line form-control'}), required=False)

    def clean(self):
        cleaned_data = super().clean()
        produkttype = cleaned_data.get('produkttype')
        if produkttype and not produkttype.fiskeart.pelagisk:
            for field in ('salgspris',):
                if cleaned_data[field] is None:
                    raise ValidationError({field: self.fields[field].error_messages['required']}, code='required')
        return cleaned_data

    class Meta:
        model = IndberetningLinje
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris', 'fartøj_navn', 'indhandlingssted', 'bonus', 'kommentar')


class IndberetningsLinjeSkema3Form(IndberetningsLinjeForm):
    produkttype = ModelChoiceField(queryset=ProduktType.objects.filter(fiskeart__skematype=3).order_by('fiskeart__pelagisk', 'navn_dk'), required=True)
    bonus = LocalizedDecimalField(initial=0)
    indhandlingssted = CharField(widget=Select(attrs={'class': "js-place-select form-control col-2 ", 'autocomplete': "off", 'style': 'width:100%'}))
    kommentar = CharField(widget=Textarea(attrs={'class': 'single-line form-control'}), required=False)

    class Meta:
        model = IndberetningLinje
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris', 'indhandlingssted', 'bonus', 'kommentar')


BilagsFormSet = modelformset_factory(Bilag, can_order=False, exclude=('uuid', 'indberetning'), extra=1)


class IndberetningBeregningForm(ModelForm):
    class Meta:
        model = Indberetning
        fields = ('afgiftsperiode', 'skematype', )


class IndberetningSearchForm(BootstrapForm):
    afgiftsperiode = ModelChoiceField(
        Afgiftsperiode.objects,
        required=False,
        empty_label=_('Alle perioder')
    )
