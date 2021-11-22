from django import forms
from django.db.models import Count
from administration.models import Afgiftsperiode, SatsTabelElement, Kvartal
from administration.forms_mixin import BootstrapForm


class AfgiftsperiodeForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = Afgiftsperiode
        fields = ('aarkvartal',)

    aarkvartal = forms.ModelChoiceField(
        queryset=Kvartal.objects.annotate(count=Count('afgiftsperiode')).filter(count=0)
    )


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

    def save_new_objects(self, commit=True):
        self.new_objects = []
        for form in self.extra_forms:
            if not form.has_changed():
                # unchanged, save anyway
                pass
            # If someone has marked an add form for deletion, don't save the
            # object.
            if self.can_delete and self._should_delete_form(form):
                continue
            self.new_objects.append(self.save_new(form, commit=commit))
            if not commit:
                self.saved_forms.append(form)
        return self.new_objects


class SatsTabelElementForm(forms.ModelForm, BootstrapForm):

    class Meta:
        model = SatsTabelElement
        fields = (
            'tabel', 'ressource', 'rate_pr_kg_indhandling', 'rate_pr_kg_export', 'rate_procent_indhandling',
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
