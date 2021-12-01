from django.core.exceptions import ValidationError
from django.forms import forms, ModelChoiceField, ChoiceField, CharField, ModelForm, modelformset_factory
from django.utils.translation import gettext as _

from administration.models import Afgiftsperiode, FiskeArt, ProduktKategori
from indberetning.models import Bilag, indberetnings_type_choices, Virksomhed, Indberetning, IndberetningLinje
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
    type = ChoiceField(choices=indberetnings_type_choices, required=True)
    periode = ModelChoiceField(queryset=Afgiftsperiode.objects.filter(vis_i_indberetning=True),
                               required=True, empty_label=None)


class IndberetningsLinjeForm(ModelForm):
    fiskeart = ModelChoiceField(queryset=FiskeArt.objects.order_by('navn'), required=True)
    kategori = ModelChoiceField(queryset=ProduktKategori.objects.order_by('navn'), required=True)
    salgsvægt = LocalizedDecimalField()
    levende_vægt = LocalizedDecimalField()
    salgspris = LocalizedDecimalField()

    def clean(self):
        cleaned_data = super().clean()
        if 'salgsvægt' and 'levende_vægt' and 'salgspris' in cleaned_data:
            numbers = (cleaned_data['salgsvægt'], cleaned_data['levende_vægt'], cleaned_data['salgspris'])
            if not (all(i > 0 for i in numbers) or all(i < 0 for i in numbers)):
                raise ValidationError(_('Salgsvægt, levende vægt og salgspris skal alle være negative eller positive tal'))

    class Meta:
        model = IndberetningLinje
        fields = ('fiskeart', 'kategori', 'salgsvægt', 'levende_vægt', 'salgspris')


class IndberetningsForm(ModelForm):

    class Meta:
        model = Indberetning
        fields = ('navn', )


IndberetningFormSet = modelformset_factory(IndberetningLinje,
                                           form=IndberetningsLinjeForm,
                                           can_delete=False,
                                           validate_min=True,
                                           extra=1)
BilagsFormSet = modelformset_factory(Bilag, can_order=False, exclude=('uuid', 'indberetning'), extra=1)
