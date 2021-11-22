from django.forms import forms, ModelChoiceField, ChoiceField, CharField, ModelForm

from administration.models import Afgiftsperiode
from indberetning.models import indberetnings_type_choices, Virksomhed


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
