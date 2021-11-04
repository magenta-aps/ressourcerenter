from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row
from django import forms
from django.forms import Textarea, modelformset_factory
from django.utils.translation import gettext as _

from . import models


class RunCalculationForm(forms.Form):
    fra_dato = forms.DateField(label=_("Dato fra"))
    til_dato = forms.DateField(label=_("Dato til"))
    beregningsmodel = forms.ModelChoiceField(models.BeregningsModelEksempel.objects.all())
    afgiftstabel = forms.ModelChoiceField(models.Afgiftstabel.objects.all(), required=True)

    def __init__(self, *args, **kwargs):
        super(RunCalculationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'myexampleform'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'beregningsmodel',
            'afgiftstabel',
            Row('fra_dato', 'til_dato')
        )


class EditFormForm(forms.Form):
    name = forms.CharField(label=_("Titel"))
    description = forms.CharField(label=_("Beskrivelse"), widget=Textarea)

    calculation_model = forms.ModelChoiceField(queryset=models.BeregningsModelPrototype.objects.all())

    felt_1 = forms.ModelChoiceField(queryset=models.FormularFelt.objects.all(), required=False)
    felt_2 = forms.ModelChoiceField(queryset=models.FormularFelt.objects.all(), required=False)
    felt_3 = forms.ModelChoiceField(queryset=models.FormularFelt.objects.all(), required=False)
    felt_4 = forms.ModelChoiceField(queryset=models.FormularFelt.objects.all(), required=False)


EditSatsFormBase = modelformset_factory(models.SatsTabelPost, fields=['kategori', 'fiskeart', 'type', 'vaerdi'], extra=6)

class EditSatsForm(EditSatsFormBase):

    def __init__(self, *args, **kwargs):
        super(EditSatsForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'myexampleform'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row('kategori', 'fiskeart', 'type', 'vaerdi')
        )


