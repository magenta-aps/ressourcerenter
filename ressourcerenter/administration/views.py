from django import forms
from django.conf import settings
from django.db.models.query import prefetch_related_objects
from django.db.models import Sum
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.views.generic import RedirectView
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin, BaseDetailView
from django.views.generic.edit import BaseFormView
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.utils.functional import cached_property
from django.http.response import FileResponse


from datetime import timedelta
from tenQ.client import ClientException
import re
from os import path
from itertools import chain
from datetime import date
from uuid import uuid4
from django.core.files import File

from administration.views_mixin import HistoryMixin
from project.views_mixin import ExcelMixin, GetFormView

from administration.forms import (
    AfgiftsperiodeForm,
    SatsTabelElementForm,
    SatsTabelElementFormSet,
)
from administration.models import Afgiftsperiode, SatsTabelElement

from administration.forms import FiskeArtForm
from administration.models import FiskeArt

from administration.forms import ProduktTypeCreateForm, ProduktTypeUpdateForm
from administration.models import ProduktType

from indberetning.models import Indberetning
from administration.forms import IndberetningSearchForm

from indberetning.models import IndberetningLinje
from administration.forms import (
    IndberetningLinjeKommentarForm,
    IndberetningLinjeKommentarFormSet,
)
from administration.forms import IndberetningAfstemForm

from indberetning.models import Virksomhed
from administration.forms import VirksomhedForm

from administration.models import Faktura, Prisme10QBatch
from administration.forms import FakturaForm, BatchSendForm

from administration.forms import G69KodeForm
from administration.models import G69Code

from administration.models import G69CodeExport

from administration.models import g69_export_filepath

from administration.forms import G69CodeExportForm


class PostLoginView(RedirectView):
    # Viderestiller til forsiden af den app man har adgang til
    def get_redirect_url(self):
        for app_name in ("administration", "statistik"):
            if self.request.user.groups.filter(name=app_name).exists():
                return reverse(f"{app_name}:frontpage")
        return reverse("indberetning:frontpage")


class FrontpageView(TemplateView):
    # TODO can be replaced, just needed a landing page.
    template_name = "administration/frontpage.html"


# region Afgiftsperiode


class AfgiftsperiodeCreateView(CreateView):

    model = Afgiftsperiode
    form_class = AfgiftsperiodeForm

    def get_success_url(self):
        # Sender direkte videre til satstabellen; vi kan overveje bare at sende til listen
        return reverse(
            "administration:afgiftsperiode-satstabel", kwargs={"pk": self.object.pk}
        )


class AfgiftsperiodeListView(ListView):

    model = Afgiftsperiode
    queryset = Afgiftsperiode.objects.all()


class AfgiftsperiodeUpdateView(UpdateView):
    form_class = AfgiftsperiodeForm
    model = Afgiftsperiode

    def get_success_url(self):
        return reverse("administration:afgiftsperiode-list")


class AfgiftsperiodeHistoryView(HistoryMixin, DetailView):

    model = Afgiftsperiode

    def get_fields(self, **kwargs):
        return ("navn_dk", "navn_gl", "vis_i_indberetning", "beregningsmodel")

    def get_back_url(self):
        return reverse("administration:afgiftsperiode-list")


class AfgiftsperiodeSatsTabelUpdateView(UpdateView):

    model = Afgiftsperiode
    form_class = forms.inlineformset_factory(
        Afgiftsperiode,
        SatsTabelElement,
        formset=SatsTabelElementFormSet,
        form=SatsTabelElementForm,
        extra=0,
        can_delete=False,
    )

    template_name = "administration/afgiftsperiode_satstabel.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        qs = (
            self.object.entries.filter(skematype__enabled=True)
            .order_by("skematype__navn_dk", "fiskeart__navn_dk", "fartoej_groenlandsk")
            .select_related("fiskeart")
        )
        kwargs.update(
            {
                "queryset": qs,
                "instance": self.object,
            }
        )
        return kwargs

    def get_success_url(self):
        return reverse("administration:afgiftsperiode-list")

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                "periode": self.object,
            }
        )


class SatsTabelElementHistoryView(HistoryMixin, DetailView):

    model = SatsTabelElement

    def get_fields(self):
        return (
            "rate_pr_kg",
            "rate_procent",
        )


# endregion


# region FiskeArt


class FiskeArtCreateView(CreateView):

    model = FiskeArt
    form_class = FiskeArtForm

    def get_success_url(self):
        return reverse("administration:fiskeart-list")

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{**kwargs, "creating": True})


class FiskeArtUpdateView(UpdateView):

    model = FiskeArt
    form_class = FiskeArtForm

    def get_success_url(self):
        return reverse("administration:fiskeart-list")


class FiskeArtListView(ListView):

    model = FiskeArt


class FiskeArtHistoryView(HistoryMixin, DetailView):

    model = FiskeArt

    def get_fields(self, **kwargs):
        return (
            "navn_dk",
            "navn_gl",
            "beskrivelse",
        )


# endregion


# region ProduktType


class ProduktTypeCreateView(CreateView):

    model = ProduktType
    form_class = ProduktTypeCreateForm

    def get_success_url(self):
        return reverse("administration:produkttype-list")

    def get_context_data(self, **kwargs):
        return super().get_context_data(**{**kwargs, "creating": True})


class ProduktTypeUpdateView(UpdateView):

    model = ProduktType
    form_class = ProduktTypeUpdateForm

    def get_success_url(self):
        return reverse("administration:produkttype-list")


class ProduktTypeListView(ListView):

    model = ProduktType


class ProduktTypeHistoryView(HistoryMixin, DetailView):

    model = ProduktType

    def get_fields(self, **kwargs):
        return ("navn_dk", "navn_gl", "beskrivelse", "fiskeart", "fartoej_groenlandsk")


class IndberetningDetailView(UpdateView):
    template_name = "administration/indberetning_detail.html"
    model = Indberetning

    form_class = forms.inlineformset_factory(
        Indberetning,
        IndberetningLinje,
        form=IndberetningLinjeKommentarForm,
        formset=IndberetningLinjeKommentarFormSet,
        can_delete=False,
        extra=0,
    )

    def get_success_url(self):
        # The list may supply its full url in the `back`-parameter,
        # so that we return to the last search results instead of the unfiltered list
        return self.request.GET.get("back", reverse("administration:indberetning-list"))


class IndberetningAfstemFormView(UpdateView):
    model = Indberetning
    form_class = IndberetningAfstemForm

    def get_success_url(self):
        return reverse(
            "administration:indberetning-detail", kwargs={"pk": self.object.pk}
        )


class IndberetningListView(ExcelMixin, ListView):
    template_name = "administration/indberetning_list.html"  # Eksplicit for at undgå navnekollision med template i indberetning
    model = Indberetning
    form_class = IndberetningSearchForm

    excel_fields = (
        (_("Afgiftsperiode"), "afgiftsperiode__navn_dk"),
        (_("Virksomhed"), "virksomhed__cvr"),
        (_("Cpr"), "indberetters_cpr"),
        (_("Indberetningstidspunkt"), "indberetningstidspunkt"),
        (_("Fiskearter"), "get_fishcategories_string"),
    )

    def get_form(self):
        return self.form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        return {
            "data": self.request.GET,
        }

    def get_queryset(self):
        form = self.get_form()
        qs = self.model.objects.all()
        if form.is_valid():
            data = form.cleaned_data
            if data["afgiftsperiode"]:
                qs = qs.filter(afgiftsperiode=data["afgiftsperiode"])
            if data["beregningsmodel"]:
                qs = qs.filter(afgiftsperiode__beregningsmodel=data["beregningsmodel"])
            if data["tidspunkt_fra"]:
                qs = qs.filter(indberetningstidspunkt__gte=data["tidspunkt_fra"])
            if data["tidspunkt_til"]:
                qs = qs.filter(
                    indberetningstidspunkt__lt=data["tidspunkt_til"] + timedelta(days=1)
                )
            if data["cvr"]:
                qs = qs.filter(
                    virksomhed__cvr__contains=re.sub(r"[^\d]", "", data["cvr"])
                )
            if data["produkttype"]:
                qs = qs.filter(linjer__produkttype=data["produkttype"])
            qs = qs.annotate(linjer_sum=Sum("linjer__fangstafgift__afgift"))
            qs = qs.order_by("-indberetningstidspunkt")
        return qs

    def get_context_data(self, **kwargs):
        for related in (
            "afgiftsperiode",
            "virksomhed",
            "linjer__produkttype__fiskeart",
            "linjer",
        ):
            prefetch_related_objects(self.object_list, related)
        return super().get_context_data(**{**kwargs, "form": self.get_form()})


class IndberetningListLinjeView(DetailView):
    template_name = "administration/indberetning_list.htmx"
    model = Indberetning

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "linjer__produkttype",
                "linjer__produkttype__fiskeart",
                "linjer__fangstafgift",
            )
        )


class FakturaDetailView(DetailView):
    template_name = "administration/faktura_detail.html"
    model = Faktura

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                "destinations_available": settings.PRISME_PUSH[
                    "destinations_available"
                ],
            }
        )


class VirksomhedListView(ListView):
    model = Virksomhed
    template_name = "administration/virksomhed_list.html"


class VirksomhedCreateView(CreateView):
    form_class = VirksomhedForm
    model = Virksomhed
    template_name = "administration/virksomhed_form.html"

    def get_success_url(self):
        return reverse("administration:virksomhed-list")

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                "creating": True,
            }
        )


class VirksomhedUpdateView(UpdateView):
    form_class = VirksomhedForm
    model = Virksomhed
    template_name = "administration/virksomhed_form.html"

    def get_success_url(self):
        return reverse("administration:virksomhed-list")


class VirksomhedRepræsentantView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse("indberetning:indberetning-list")

    def get(self, request, *args, **kwargs):
        try:
            virksomhed = Virksomhed.objects.get(pk=kwargs["pk"])
        except Virksomhed.DoesNotExist:
            return HttpResponseNotFound
        request.session["cvr"] = virksomhed.cvr
        request.session["impersonating"] = True
        return super().get(request, *args, **kwargs)


class VirksomhedRepræsentantStopView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        for key in ("cvr", "impersonating"):
            try:
                del self.request.session[key]
            except KeyError:
                pass

        if settings.OPENID.get("mock") == "cvr":
            self.request.session["cvr"] = "12345678"

        return reverse("administration:virksomhed-list")


class FakturaCreateView(CreateView):
    form_class = FakturaForm
    template_name = "administration/faktura_form.html"
    model = IndberetningLinje

    def get_form_kwargs(self):
        linje = self.get_object()
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "opkrævningsdato": Faktura.get_opkrævningsdato(
                linje.indberetningstidspunkt.date()
            ),
            "betalingsdato": Faktura.get_betalingsdato(date.today()),
        }
        return kwargs

    def get_success_url(self):
        return reverse("administration:indberetningslinje-list")

    def get_context_data(self, **kwargs):
        destinations_available = settings.PRISME_PUSH["destinations_available"]
        return super().get_context_data(
            **{
                **kwargs,
                # Option to send to test is only avaliable when both are possible
                "send_to_test_available": destinations_available["10q_production"]
                and destinations_available["10q_development"],
            }
        )

    def form_valid(self, form):
        linje = self.get_object()
        faktura = Faktura.objects.create(
            kode=linje.debitorgruppekode,
            periode=linje.indberetning.afgiftsperiode,
            virksomhed=linje.indberetning.virksomhed,
            beløb=linje.afgift,
            opretter=self.request.user,
            batch=Prisme10QBatch.objects.create(oprettet_af=self.request.user),
            betalingsdato=form.cleaned_data["betalingsdato"],
            opkrævningsdato=form.cleaned_data["opkrævningsdato"],
        )
        linje.faktura = faktura
        linje.save(update_fields=("faktura",))

        try:
            faktura.batch.send(self.request.user, form.cleaned_data["send_to_test"])
        except ClientException as e:
            # Exception message has been saved to batch.fejlbesked
            messages.add_message(
                self.request,
                messages.INFO,
                _("Faktura oprettet, men afsendelse fejlede: {error}").format(
                    error=str(e)
                ),
            )
            raise
        else:
            messages.add_message(
                self.request, messages.INFO, _("Faktura oprettet og afsendt")
            )

        return redirect(self.get_success_url())


class FakturaSendView(SingleObjectMixin, BaseFormView):

    form_class = BatchSendForm
    model = Faktura

    def form_valid(self, form):
        try:
            self.get_object().batch.send(
                self.request.user, form.cleaned_data["destination"] == "10q_development"
            )
        except ClientException as e:
            # Exception message has been saved to batch.fejlbesked
            messages.add_message(
                self.request,
                messages.INFO,
                _("Afsendelse fejlede: {error}").format(error=str(e)),
            )
        else:
            messages.add_message(self.request, messages.INFO, _("Faktura afsendt"))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.INFO,
            _("Afsendelse fejlede: {error}").format(
                error=", ".join(chain(*form.errors.values()))
            ),
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "administration:faktura-detail", kwargs={"pk": self.get_object().pk}
        )


class IndberetningsLinjeListView(TemplateView):
    template_name = "administration/indberetning_afstem.html"

    # TODO: Skal indberetninger være afstemt før vi kan lave en faktura?

    @cached_property
    def periode(self):
        periode_id = self.request.GET.get("periode")
        if periode_id:
            try:
                return Afgiftsperiode.objects.get(pk=periode_id)
            except Afgiftsperiode.DoesNotExist:
                pass
        return Afgiftsperiode.objects.first()

    @cached_property
    def data(self):
        # Opret et træ som grupperer indberetningslinjer i:
        # * Virksomheder
        # * Produkttyper
        # * Fangsttyper
        virksomheder = []
        sum_fields = {"produktvægt", "levende_vægt", "salgspris", "afgift"}

        virksomheder_uuids = [
            virksomhed["virksomhed"]
            for virksomhed in Indberetning.objects.filter(afgiftsperiode=self.periode)
            .values("virksomhed")
            .distinct()
        ]
        for virksomhed in Virksomhed.objects.filter(
            uuid__in=virksomheder_uuids
        ).prefetch_related("indberetning_set", "indberetning_set__linjer"):

            virksomhed_data = {"virksomhed": virksomhed, "produkttyper": {}}
            virksomheder.append(virksomhed_data)
            for indberetning in virksomhed.indberetning_set.filter(
                afgiftsperiode=self.periode
            ).select_related("skematype"):
                for linje in (
                    indberetning.linjer.all()
                    .select_related(
                        "faktura",
                        "produkttype",
                        "fangstafgift",
                        "produkttype__gruppe",
                        "indhandlingssted",
                    )
                    .order_by("produkttype", "-indberetningstidspunkt", "uuid")
                ):
                    produkttype = linje.produkttype
                    if produkttype.uuid not in virksomhed_data["produkttyper"]:
                        virksomhed_data["produkttyper"][produkttype.uuid] = {
                            "produkttype": produkttype,
                            "fangsttyper": {},
                        }
                    produkttype_item = virksomhed_data["produkttyper"][produkttype.uuid]

                    fangsttype = linje.fangsttype
                    if fangsttype not in produkttype_item["fangsttyper"]:
                        produkttype_item["fangsttyper"][fangsttype] = {
                            "sum": {key: 0 for key in sum_fields},
                            "linjer": [],
                        }
                    fangsttype_item = produkttype_item["fangsttyper"][fangsttype]

                    for key in sum_fields:
                        fangsttype_item["sum"][key] += getattr(linje, key)
                    fangsttype_item["linjer"].append(linje)
        return virksomheder

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **{
                **kwargs,
                "data": self.data,
                "afgiftsperioder": Afgiftsperiode.objects.all(),
                "periode": self.periode,
            }
        )


class G69ExcelView(ExcelMixin):
    template_name = "administration/g69kode_form.html"
    filename_base = "g69_koder"

    excel_fields = [
        (_("G69-Kode"), "kode"),
        (_("År"), "skatteår"),
        (_("Fangsttype"), "fangsttype"),
        (_("Aktivitetskode"), "aktivitet_kode"),
        (_("Fiskeart"), "fiskeart_navn"),
        (_("Fiskeart kode"), "fiskeart_kode"),
        (_("Sted"), "sted_navn"),
        (_("Stedkode"), "sted_kode"),
    ]

    def headers(self, form):
        return [header_name for key, header_name in G69Code.get_spreadsheet_headers()]

    def rows(self, form):
        headers = G69Code.get_spreadsheet_headers()
        data = G69Code.get_spreadsheet_raw(form.cleaned_data["år"], collapse=True)[
            "data"
        ]
        return [[item[key] for key, header_name in headers] for item in data]


class G69DirectDownloadView(G69ExcelView, GetFormView):
    form_class = G69KodeForm

    def form_valid(self, form):
        return self.render_excel_file({"form": form})


class G69CodeExportCreateView(G69ExcelView, CreateView):
    model = G69CodeExport
    form_class = G69CodeExportForm
    success_url = reverse_lazy("administration:g69-list")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        filename = g69_export_filepath(self.object, uuid4())
        full_path = path.join(settings.MEDIA_ROOT, filename)
        self.create_excel_file({"form": form}, full_path)
        with open(full_path, mode="rb") as f:
            self.object.excel_file = File(f, name=f"export_{self.object.år}.xlsx")
            self.object.save()
        return super().form_valid(form)


class G69ListView(ListView):
    model = G69CodeExport
    template_name = "administration/g69kode_list.html"


class G69DownloadView(BaseDetailView):
    model = G69CodeExport

    def render_to_response(self, context):
        response = FileResponse(
            self.object.excel_file, as_attachment=True, filename="g69_koder.xlsx"
        )
        # response['Content-Disposition'] = f"attachment; filename={self.object.år}.xlsx"
        return response
