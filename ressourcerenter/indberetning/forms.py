from django.core.exceptions import ValidationError
from django.forms import forms, ModelChoiceField, CharField, ModelForm, modelformset_factory, Select
from django.utils.translation import gettext as _


from administration.models import Afgiftsperiode, ProduktType, SkemaType
from indberetning.models import Bilag, Virksomhed, IndberetningLinje, Navne
from project.form_fields import LocalizedDecimalField


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
        fields = ('kontakt_person', 'kontakt_email',
                  'kontakts_phone_nr')


class IndberetningsTypeSelectForm(forms.Form):
    skema = ModelChoiceField(queryset=SkemaType.objects.all(), required=True)
    periode = ModelChoiceField(queryset=Afgiftsperiode.objects.filter(vis_i_indberetning=True),
                               required=True, empty_label=None)


class IndberetningsLinjeForm(ModelForm):
    salgsvægt = LocalizedDecimalField()
    levende_vægt = LocalizedDecimalField()
    salgspris = LocalizedDecimalField(required=False)
    pelagisk_nonrequired_fields = ()

    def __init__(self, *args, **kwargs):
        self.cvr = kwargs.pop('cvr')
        super().__init__(*args, **kwargs)
        self.fields['fartøj_navn'].widget.choices = [(n.navn, n.navn) for n in Navne.objects.filter(virksomhed__cvr=self.cvr, type='fartøj')]

    def clean(self):
        cleaned_data = super().clean()
        if ('salgsvægt' in cleaned_data or 'levende_vægt' in cleaned_data) and 'salgspris' in cleaned_data:
            numbers = filter(None, (cleaned_data['salgsvægt'], cleaned_data['levende_vægt'], cleaned_data['salgspris']))
            if not (all(i > 0 for i in numbers) or all(i < 0 for i in numbers)):
                raise ValidationError(_('Salgsvægt, levende vægt og salgspris skal alle være negative eller positive tal'))
        return cleaned_data

    class Meta:
        model = IndberetningLinje
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris', 'fartøj_navn', 'indhandlingssted')


class IndberetningsLinjeSkema1Form(IndberetningsLinjeForm):
    produkttype = ModelChoiceField(queryset=ProduktType.objects.filter(fiskeart__skematype=1).order_by('navn_dk'), required=True)
    transporttillæg = LocalizedDecimalField()
    fartøj_navn = CharField(widget=Select(attrs={'class': "js-boat-select form-control col-2 ", 'autocomplete': "off", 'style': 'width:100%'}))

    def clean(self):
        cleaned_data = super().clean()
        produkttype = cleaned_data.get('produkttype')
        if produkttype and not cleaned_data['produkttype'].fiskeart.pelagisk:
            for field in ('salgspris', 'transporttillæg'):
                if cleaned_data[field] is None:
                    raise ValidationError({field: self.fields[field].error_messages['required']}, code='required')
        return cleaned_data

    class Meta:
        model = IndberetningLinje
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris', 'fartøj_navn', 'transporttillæg')


class IndberetningsLinjeSkema2Form(IndberetningsLinjeForm):
    produkttype = ModelChoiceField(queryset=ProduktType.objects.filter(fiskeart__skematype=2).order_by('navn_dk'), required=True)
    bonus = LocalizedDecimalField()
    fartøj_navn = CharField(widget=Select(attrs={'class': "js-boat-select form-control col-2 ", 'autocomplete': "off", 'style': 'width:100%'}))
    indhandlingssted = CharField(widget=Select(attrs={'class': "js-place-select form-control col-2 ", 'autocomplete': "off", 'style': 'width:100%'}))

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
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris', 'fartøj_navn', 'indhandlingssted', 'bonus')


class IndberetningsLinjeSkema3Form(IndberetningsLinjeForm):
    produkttype = ModelChoiceField(queryset=ProduktType.objects.filter(fiskeart__skematype=3).order_by('navn_dk'), required=True)
    bonus = LocalizedDecimalField()
    indhandlingssted = CharField(widget=Select(attrs={'class': "js-place-select form-control col-2 ", 'autocomplete': "off", 'style': 'width:100%'}))

    class Meta:
        model = IndberetningLinje
        fields = ('produkttype', 'salgsvægt', 'levende_vægt', 'salgspris', 'indhandlingssted', 'bonus')


BilagsFormSet = modelformset_factory(Bilag, can_order=False, exclude=('uuid', 'indberetning'), extra=1)
