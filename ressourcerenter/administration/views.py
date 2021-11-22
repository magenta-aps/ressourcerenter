from django import forms
from django.utils.functional import cached_property
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse
from administration.forms import AfgiftsperiodeForm, SatsTabelElementForm, SatsTabelElementFormSet
from administration.models import Afgiftsperiode, Ressource, SatsTabelElement


class FrontpageView(TemplateView):
    # TODO can be replaced, just needed a landing page.
    template_name = 'administration/frontpage.html'


class AfgiftsperiodeCreateView(CreateView):
    model = Afgiftsperiode
    form_class = AfgiftsperiodeForm

    def get_success_url(self):
        # Sender direkte videre til satstabellen; vi kan overveje bare at sende til listen
        return reverse('administration:afgiftsperiode-satstabel', kwargs={'pk': self.object.pk})


class AfgiftsperiodeListView(ListView):
    model = Afgiftsperiode
    queryset = Afgiftsperiode.objects.all()


class SatsTabelUpdateView(UpdateView):

    model = Afgiftsperiode
    form_class = forms.inlineformset_factory(
        Afgiftsperiode,
        SatsTabelElement,
        formset=SatsTabelElementFormSet,
        form=SatsTabelElementForm,
        extra=0,
        can_delete=False
    )

    template_name = 'administration/afgiftsperiode_satstabel.html'

    @cached_property
    def resources(self):
        return Ressource.objects.all().order_by('fiskeart__navn', 'fiskeart__navn')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'form_kwargs': {
                'ressourcer': list(self.resources)
            },
            'queryset': self.object.entries.order_by('ressource__fiskeart__navn', 'ressource__fangsttype__navn'),
            'min_num': len(self.resources),
            'instance': self.object,
        })
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_initial(self):
        return [
            {'ressource': ressource}
            for ressource in self.resources
        ]

    def get_success_url(self):
        return reverse('administration:afgiftsperiode-list')

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{
            **kwargs,
            'tabel': self.object,
        })
