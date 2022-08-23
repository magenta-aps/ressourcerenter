import json
import mimetypes
from administration.models import Afgiftsperiode, SkemaType, FiskeArt, ProduktType
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Sum
from django.db.models.query import prefetch_related_objects
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import (
    RedirectView,
    ListView,
    FormView,
    View,
    DetailView,
    UpdateView,
)
from indberetning.forms import (
    IndberetningsTypeSelectForm,
    VirksomhedsAddressForm,
    BilagsFormSet,
    IndberetningsLinjeSkema1Form,
    IndberetningsLinjeSkema2Form,
    IndberetningsLinjeSkema3Form,
    IndberetningBeregningForm,
    IndberetningsLinjeBeregningForm,
    IndberetningSearchForm,
)
from indberetning.models import Indberetning, Virksomhed, IndberetningLinje, Bilag

LoginProvider = import_string(settings.LOGIN_PROVIDER_CLASS)


class Frontpage(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        cvr = self.request.session.get("cvr")
        if cvr:
            try:
                virksomhed, created = Virksomhed.objects.get_or_create(cvr=cvr)
            except IntegrityError:
                # virksomhed exists so get it
                created = False
                virksomhed = Virksomhed.objects.get(cvr=cvr)

            virksomhed_navn = self.request.session["user_info"]["OrganizationName"]
            if virksomhed.navn is None:
                virksomhed.navn = virksomhed_navn
                virksomhed.save(update_fields=["navn"])
            elif virksomhed.navn != virksomhed_navn:
                # What to do when data from login doesn't match DB?
                self.request.session["user_info"]["OrganizationName"] = virksomhed.navn

            if created:
                # Hvis cvr nummeret lige er blevet oprettet,
                # redirect til redigering af administrativ adresse.
                return reverse(
                    "indberetning:company-edit", kwargs={"pk": virksomhed.uuid}
                )
            return reverse("indberetning:indberetning-list")
        return reverse("indberetning:login")


class VirksomhedUpdateView(UpdateView):
    model = Virksomhed
    form_class = VirksomhedsAddressForm

    def get_success_url(self):
        return reverse("indberetning:indberetning-list")


class IndberetningsListView(ListView):

    form_class = IndberetningSearchForm

    def get_queryset(self):
        qs = Indberetning.objects.filter(
            virksomhed__cvr=self.request.session["cvr"]
        ).order_by("-indberetningstidspunkt")
        form = self.get_form()
        if form.is_valid():
            data = form.cleaned_data
            if data["afgiftsperiode"]:
                qs = qs.filter(afgiftsperiode=data["afgiftsperiode"])

        qs = qs.annotate(linjer_sum=Sum("linjer__fangstafgift__afgift"))
        return qs

    def get_form(self):
        return self.form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        return {
            "data": self.request.GET,
        }

    def get_context_data(self, **kwargs):
        for related in (
            "afgiftsperiode",
            "virksomhed",
            "skematype",
            "bilag",
        ):
            prefetch_related_objects(self.object_list, related)
        return super().get_context_data(**{**kwargs, "form": self.get_form()})


class IndberetningListLinjeView(DetailView):
    template_name = "indberetning/indberetning_list.htmx"
    model = Indberetning
    context_object_name = "indberetning"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "linjer__produkttype",
                "linjer__produkttype__fiskeart",
                "linjer__fangstafgift",
                "linjer__indhandlingssted",
            )
        )


class SelectIndberetningsType(FormView):
    form_class = IndberetningsTypeSelectForm
    template_name = "indberetning/type_select.html"

    def form_valid(self, form):
        periode_uuid = form.cleaned_data["periode"].uuid
        skema_id = form.cleaned_data["skema"].id

        return HttpResponseRedirect(
            reverse(
                "indberetning:indberetning-create",
                kwargs={"periode": periode_uuid, "skema": skema_id},
            )
        )


class IndberetningsLinjebilagFormsetMixin:
    def get_linje_form(self):
        if self.skema.id == 1:
            return IndberetningsLinjeSkema1Form
        if self.skema.id == 2:
            return IndberetningsLinjeSkema2Form
        if self.skema.id == 3:
            return IndberetningsLinjeSkema3Form

    def get_form_class(self):
        formset_class = inlineformset_factory(
            parent_model=Indberetning,
            model=IndberetningLinje,
            form=self.get_linje_form(),
            can_delete=False,
            validate_min=True,
            extra=1,
        )
        return formset_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "prefix": "linje",
                "auto_id": False,
                "form_kwargs": {"cvr": self.request.session["cvr"]},
            }
        )
        if "data" not in kwargs:
            kwargs["queryset"] = IndberetningLinje.objects.none()
        return kwargs

    def get_context_data(self, **kwargs):
        if "bilag_formset" not in kwargs:
            kwargs["bilag_formset"] = BilagsFormSet(
                auto_id=False, prefix="bilag", queryset=Bilag.objects.none()
            )
        ctx = super(IndberetningsLinjebilagFormsetMixin, self).get_context_data(
            **kwargs
        )
        ctx["indberetning"] = self.get_indberetning_instance()
        ctx["pelagiske_fiskearter"] = [
            str(uuid)
            for uuid in FiskeArt.objects.filter(pelagisk=True).values_list(
                "uuid", flat=True
            )
        ]
        ctx["pelagiske_produkttyper"] = [
            str(uuid)
            for uuid in ProduktType.objects.filter(fiskeart__pelagisk=True).values_list(
                "uuid", flat=True
            )
        ]
        return ctx

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        bilag_formset = BilagsFormSet(
            request.POST, request.FILES, auto_id=False, prefix="bilag"
        )
        if form.is_valid() and bilag_formset.is_valid():
            return self.form_valid(form, bilag_formset)
        else:
            return self.form_invalid(form, bilag_formset)

    def form_valid(self, formset, bilag_formset):
        linjer = []
        for line in formset.save(commit=False):
            linjer.append(line)
        bilags = []
        for bilag in bilag_formset.save(commit=False):
            bilags.append(bilag)
        # Only create indberetning if there are lines or attachments
        if linjer or bilags:
            indberetning = self.get_indberetning_instance()
            indberetning.save()
            # need to set FK
            for line in linjer:
                line.indberetning = indberetning
                line.save()
            for bilag in bilags:
                bilag.indberetning = indberetning
                bilag.save()
        return linjer, bilags

    def form_invalid(self, formset, bilag_formset):
        return self.render_to_response(
            self.get_context_data(form=formset, bilag_formset=bilag_formset)
        )


class CreateIndberetningCreateView(IndberetningsLinjebilagFormsetMixin, FormView):
    """
    Create view for kystnært (fartøj)/pelagisk (havgående) fiskeri og måske flere.
    """

    template_name = "indberetning/indberetning_form.html"

    @cached_property
    def afgiftsperiode(self):
        return Afgiftsperiode.objects.get(uuid=self.kwargs["periode"])

    @cached_property
    def skema(self):
        return SkemaType.objects.get(id=self.kwargs["skema"])

    def get_indberetning_instance(self):
        """
        :return: an unsaved instance of indberetning with th virksomhed and afgiftsperiode etc set
        """
        instance = Indberetning(
            virksomhed=Virksomhed.objects.get(cvr=self.request.session["cvr"]),
            afgiftsperiode=self.afgiftsperiode,
            skematype=self.skema,
        )
        if self.request.user.is_authenticated:
            # if the user is logged in as an administrator set the administrator field.
            instance.administrator = self.request.user
        else:
            # nemid bruger indberetter
            instance.indberetters_cpr = self.request.session.get("cpr") or "-"
        return instance

    def get_context_data(self, **kwargs):
        ctx = super(CreateIndberetningCreateView, self).get_context_data(**kwargs)
        ctx.update(
            {
                "form_url": reverse(
                    "indberetning:indberetning-create",
                    kwargs={
                        "periode": self.afgiftsperiode.uuid,
                        "skema": self.skema.id,
                    },
                ),
                "afgiftsperiode": self.afgiftsperiode,
                "skema": self.skema,
            }
        )
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(CreateIndberetningCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, formset, bilag_formset):
        linjer, bilags = super(CreateIndberetningCreateView, self).form_valid(
            formset, bilag_formset
        )
        fiskearter = set([str(linje.produkttype) for linje in linjer])
        message = _("Ny Indberetning oprettet for: %s.") % ", ".join(fiskearter)
        if len(bilags) > 0:
            message = _(
                "Ny Indberetning oprettet for: %(fiskearter)s med %(bilag)s bilag."
            ) % {"fiskearter": ", ".join(fiskearter), "bilag": len(bilags)}
        if len(bilags) > 0 or len(linjer) > 0:
            messages.add_message(self.request, messages.INFO, message)
        return redirect(reverse("indberetning:indberetning-list"))


class UpdateIndberetningsView(IndberetningsLinjebilagFormsetMixin, UpdateView):
    template_name = "indberetning/indberetning_form.html"

    @cached_property
    def skema(self):
        return self.object.skematype

    def get_indberetning_instance(self):
        return self.object

    @cached_property
    def afgiftsperiode(self):
        return self.get_object().afgiftsperiode

    def get_queryset(self):
        # always limit the QS to indberetninger belonging to the company.
        # check for session['cvr'] is done in middleware,
        # so we can always assume it is set when processing the view
        return Indberetning.objects.filter(
            virksomhed__cvr=self.request.session["cvr"]
        ).select_related("afgiftsperiode")

    def get_context_data(self, **kwargs):
        ctx = super(UpdateIndberetningsView, self).get_context_data(**kwargs)
        ctx.update(
            {
                "edit_mode": True,
                "form_url": reverse(
                    "indberetning:indberetning-edit",
                    kwargs={"pk": self.get_object().uuid},
                ),
                "afgiftsperiode": self.afgiftsperiode,
                "skema": self.skema,
            }
        )
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(UpdateIndberetningsView, self).post(request, *args, **kwargs)

    def form_valid(self, formset, bilag_formset):
        linjer, bilags = super(UpdateIndberetningsView, self).form_valid(
            formset, bilag_formset
        )
        message = None
        if linjer and bilags:
            message = _("Indberetningen blev justeret og tilføjet %d nye bilag.") % len(
                bilags
            )
        elif bilags:
            message = _("Der blev tilføjet %d nye bilag til indberetningen") % len(
                bilags
            )
        elif linjer:
            message = _("Indberetningen blev justeret.")

        if message:
            messages.add_message(self.request, messages.INFO, message)
        return redirect(reverse("indberetning:indberetning-list"))


class BilagDownloadView(DetailView):
    def get_queryset(self):
        return Bilag.objects.filter(
            indberetning__virksomhed__cvr=self.request.session["cvr"]
        )

    def render_to_response(self, context, **response_kwargs):
        bilag = self.get_object()
        file = bilag.bilag
        mime_type, _ = mimetypes.guess_type(file.name)
        response = HttpResponse(file.read(), content_type=mime_type)
        response["Content-Disposition"] = "attachment; filename=%s" % bilag.filename
        return response


class MultipleFormView(View):
    def get_form_classes(self):
        return self.form_classes

    def get_forms(self):
        kwargs = self.get_forms_kwargs()
        form_classes = self.get_form_classes()
        if len(form_classes) != len(kwargs):
            raise Exception("Incorrect number of form classes and kwarg dicts")
        return [form_class(**kwargs[i]) for i, form_class in enumerate(form_classes)]

    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        if all([form.is_valid() for form in forms]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)

    def get_forms_kwargs(self):
        return [self.get_form_kwargs(form_class) for form_class in self.form_classes]

    def get_form_kwargs(self, form_class):
        kwargs = {
            # 'initial': self.get_initial(),
            # 'prefix': self.get_prefix(),
        }
        if self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        if hasattr(self, "object"):
            kwargs.update({"instance": self.object})
        return kwargs


class IndberetningCalculateJsonView(MultipleFormView):

    form_classes = [IndberetningBeregningForm, IndberetningsLinjeBeregningForm]

    def forms_valid(self, forms):
        indberetning, linje = (form.save(False) for form in forms)
        linje.indberetning = indberetning
        fangstafgift = linje.calculate_afgift()
        return HttpResponse(json.dumps(fangstafgift.to_json()))

    def forms_invalid(self, forms):
        return HttpResponseBadRequest(
            json.dumps([form.errors.get_json_data() for form in forms])
        )


class LoginView(View):
    def get(self, request):
        # Setup the oauth login url and redirect the browser to it.
        provider = LoginProvider.from_settings()
        request.session["login_method"] = provider.name
        return HttpResponseRedirect(provider.login(request))


class LoginCallbackView(View):
    def get(self, request):
        provider = LoginProvider.from_settings()
        if provider.handle_login_callback(request=request):
            # if the call back was successfully, redirect to frontpage
            return HttpResponseRedirect(reverse("indberetning:frontpage"))
        return HttpResponseRedirect(reverse("indberetning:login"))


class LogoutView(View):
    def get(self, request):
        provider = LoginProvider.from_settings()
        return HttpResponseRedirect(provider.logout(request))


class LogoutCallback(View):
    @xframe_options_exempt
    def get(self, request):
        provider = LoginProvider.from_settings()
        provider.handle_logout_callback(request)
        return HttpResponse("")
