from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView, ListView
from django.views.generic.base import TemplateView

from . import forms
from .models import Afgiftsperiode
from .models import BeregningsModelEksempel
from .models import FiskeArt
from .models import FormularFelt
from .models import SummeretBeregnetIndberetning


class RunCalculationView(FormView):
    template_name = "resmockup/form.html"
    form_class = forms.RunCalculationForm
    extra_context = {
        'title': 'Kør beregning',
        'form_button_text': 'Kør'
    }


class ListSimulationView(ListView):
    template_name = "resmockup/simlist.html"
    model = SummeretBeregnetIndberetning
    extra_context = {
        'title': 'Beregning'
    }


class ListCalculationView(ListView):
    template_name = "resmockup/calclist.html"
    model = BeregningsModelEksempel
    extra_context = {
        'title': 'Beregningsmodeller'
    }


class CreateCalculationView(CreateView):
    template_name = "resmockup/form.html"
    model = BeregningsModelEksempel
    fields = ['prototype']
    extra_context = {
        'title': 'Opret beregningsmodel',
        'form_button_text': "Næste",
        'form_button_url': reverse_lazy('calc-edit')
    }

class EditCalculationView(CreateView):
    template_name = "resmockup/form.html"
    model = BeregningsModelEksempel
    fields = ['prototype', 'navn', 'beskrivelse', 'justering_A', 'justering_B']
    extra_context = {
        'title': 'Opret beregningsmodel',
        'form_button_text': "Gem"
    }


class EditFormFieldView(CreateView):
    template_name = "resmockup/form.html"
    model = FormularFelt
    fields = ["navn", "type", "valideringsregel"]
    title = "Redigér formularfelt"
    extra_context = {
        'title': "Redigér formularfelt"
    }


class EditFishView(CreateView):
    template_name = "resmockup/form.html"
    model = FiskeArt
    fields = ["navn"]
    extra_context = {
        'title': "Redigér fiskeart"
    }


class EditFormView(FormView):
    template_name = "resmockup/form.html"
    form_class = forms.EditFormForm


class EditPeriodView(CreateView):
    template_name = "resmockup/form.html"
    model = Afgiftsperiode
    extra_context = {
        'title': "Opret afgiftsperiode",
        'fields': ["simuleret", "navn", "dato_fra", "dato_til", "beskrivelse", "beregningsmodel", "afgiftstabel"]
    }


class ListPeriodView(ListView):
    template_name = "resmockup/list.html"
    model = Afgiftsperiode
    extra_context = {
        'title': "Afgiftsperioder",
        'fields': ['navn', 'dato_fra', 'dato_til']
    }


class EditSatsView(TemplateView):
    template_name = "resmockup/sats.html"
    # form_class = forms.EditSatsForm


class CreateReportView(TemplateView):
    template_name = "resmockup/report.html"


class CreateReportView1(TemplateView):
    template_name = "resmockup/report1.html"


class CreateReportView2(TemplateView):
    template_name = "resmockup/report2.html"


class CreateReportView3(TemplateView):
    template_name = "resmockup/report3.html"


class CreateReportView4(TemplateView):
    template_name = "resmockup/report4.html"
