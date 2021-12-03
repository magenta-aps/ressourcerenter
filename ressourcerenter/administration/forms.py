from django import forms
from administration.models import Afgiftsperiode, SatsTabelElement
from administration.models import FiskeArt
from administration.models import ProduktKategori
from administration.forms_mixin import BootstrapForm
from project.form_fields import DateInput


class AfgiftsperiodeForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = Afgiftsperiode
        fields = ('dato_fra', 'dato_til', 'navn')

        widgets = {
            'navn': forms.widgets.TextInput(),
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
        fields = ('navn', 'beskrivelse',)

        widgets = {
            'navn': forms.TextInput(),
            'beskrivelse': forms.TextInput(),
        }


class ProduktKategoriForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = ProduktKategori
        fields = ('navn', 'beskrivelse',)

        widgets = {
            'navn': forms.TextInput(),
            'beskrivelse': forms.TextInput(),
        }


class SatsTabelElementFormSet(forms.BaseInlineFormSet):

    def __init__(self, initial=None, min_num=None, **kwargs):
        super(SatsTabelElementFormSet, self).__init__(initial=initial, **kwargs)
        if min_num is not None:
            self.min_num = min_num

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        ressourcer = kwargs.pop('ressourcer')
        kwargs['ressource'] = ressourcer[index]
        return kwargs


class SatsTabelElementForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = SatsTabelElement
        fields = (
            'periode', 'ressource', 'rate_pr_kg_indhandling', 'rate_pr_kg_export', 'rate_procent_indhandling',
            'rate_procent_export', 'rate_prkg_groenland', 'rate_prkg_udenlandsk'
        )
        widgets = {
            'ressource': forms.HiddenInput(),
            'rate_pr_kg_indhandling': forms.NumberInput(),
            'rate_pr_kg_export': forms.NumberInput(),
            'rate_procent_indhandling': forms.NumberInput(),
            'rate_procent_export': forms.NumberInput(),
            'rate_prkg_groenland': forms.NumberInput(),
            'rate_prkg_udenlandsk': forms.NumberInput(),
        }

    def __init__(self, *args, ressource, initial=None, **kwargs):
        super(SatsTabelElementForm, self).__init__(*args, initial=initial, **kwargs)
        self.ressource_obj = ressource
