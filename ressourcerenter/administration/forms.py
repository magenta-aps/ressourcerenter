from collections import OrderedDict
from django import forms
from django.utils.functional import cached_property
from administration.models import Afgiftsperiode, SatsTabelElement
from administration.models import FiskeArt
from administration.models import SkemaType
from administration.models import ProduktType
from administration.forms_mixin import BootstrapForm
from project.form_fields import DateInput


class AfgiftsperiodeForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = Afgiftsperiode
        fields = ('dato_fra', 'dato_til', 'navn', 'beregningsmodel')

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
        by_skematype = OrderedDict()
        for skematype in SkemaType.objects.all():
            by_skematype[skematype.id] = {'forms': [], 'skematype': skematype}
        for form in self.forms:
            form_skematype = form.instance.skematype if form.instance else form.data.get('skematype')
            if form_skematype and form_skematype.id in by_skematype:
                by_skematype[form_skematype.id]['forms'].append(form)
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
