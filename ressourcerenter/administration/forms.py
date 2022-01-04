from django import forms
from django.utils.functional import cached_property
from administration.models import Afgiftsperiode, SatsTabelElement, BeregningsModel
from administration.models import FiskeArt
from administration.models import SkemaType
from administration.models import ProduktType
from project.forms_mixin import BootstrapForm
from project.form_fields import DateInput
from indberetning.models import Indberetning
from indberetning.models import IndberetningLinje


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
        by_skematype = {}
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
