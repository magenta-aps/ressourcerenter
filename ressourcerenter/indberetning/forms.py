from administration.models import Afgiftsperiode, ProduktType, SkemaType
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, CharField, FileField, BaseInlineFormSet
from django.forms import ModelForm, modelformset_factory
from django.forms import Select, Textarea, FileInput
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from indberetning.models import (
    Bilag,
    Virksomhed,
    IndberetningLinje,
    Navne,
    Indberetning,
    Indhandlingssted,
)
from project.form_fields import LocalizedDecimalField
from project.forms_mixin import BootstrapForm


class VirksomhedsAddressForm(ModelForm):
    kontakt_person = CharField(required=False)
    kontakt_email = CharField(required=False)
    kontakts_phone_nr = CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(VirksomhedsAddressForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Virksomhed
        fields = ("kontakt_person", "kontakt_email", "kontakts_phone_nr", "sted")


class IndberetningsTypeSelectForm(BootstrapForm):
    skema = ModelChoiceField(
        queryset=SkemaType.objects.filter(enabled=True), required=True
    )
    periode = ModelChoiceField(
        queryset=Afgiftsperiode.objects.filter(vis_i_indberetning=True),
        required=True,
        empty_label=None,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default to the period for todays date
        today = timezone.now().date()
        current_periode = Afgiftsperiode.objects.filter(
            dato_fra__lte=today, dato_til__gt=today
        ).first()
        if current_periode:
            self.fields["periode"].initial = current_periode.uuid


class IndberetningsLinjeBeregningForm(ModelForm):
    """
    Basisform til on-the-fly beregninger
    """

    class Meta:
        model = IndberetningLinje
        fields = (
            "produkttype",
            "produktvægt",
            "levende_vægt",
            "salgspris",
            "transporttillæg",
            "bonus",
        )

    produktvægt = LocalizedDecimalField(
        required=False,
        clientside_formatting=True,
        max_value=999_999_999,
        min_value=-999_999_999,
    )
    levende_vægt = LocalizedDecimalField(
        clientside_formatting=True, max_value=999_999_999, min_value=-999_999_999
    )
    salgspris = LocalizedDecimalField(
        required=False,
        clientside_formatting=True,
        max_value=999_999_999,
        min_value=-999_999_999,
    )
    transporttillæg = LocalizedDecimalField(
        required=False,
        clientside_formatting=True,
        max_value=999_999_999,
        min_value=-999_999_999,
    )
    bonus = LocalizedDecimalField(
        required=False,
        clientside_formatting=True,
        max_value=999_999_999,
        min_value=-999_999_999,
    )

    def clean(self):
        cleaned_data = super().clean()
        if (
            "produktvægt" in cleaned_data or "levende_vægt" in cleaned_data
        ) and "salgspris" in cleaned_data:
            numbers = list(
                filter(
                    None,
                    (
                        cleaned_data.get("produktvægt"),
                        cleaned_data.get("levende_vægt"),
                        cleaned_data["salgspris"],
                    ),
                )
            )
            if not (all(i > 0 for i in numbers) or all(i < 0 for i in numbers)):
                raise ValidationError(
                    _(
                        "Produktvægt, levende vægt og salgspris skal alle være negative eller positive tal"
                    )
                )
        if cleaned_data.get("salgspris"):
            cleaned_data["salgspris"] = round(cleaned_data["salgspris"], 0)
        return cleaned_data


class IndberetningsLinjeForm(BootstrapForm, IndberetningsLinjeBeregningForm):
    """
    Basisform til indberetningslinjer
    """

    def __init__(self, *args, **kwargs):
        self.cvr = kwargs.pop("cvr")
        super().__init__(*args, **kwargs)
        if "fartøj_navn" in self.fields:
            self.fields["fartøj_navn"].widget.choices = [
                (n.navn, n.navn)
                for n in Navne.objects.filter(virksomhed__cvr=self.cvr, type="fartøj")
            ]
        for field in self.fields.values():
            if field.required:
                field.widget.attrs["required"] = "required"

    class Meta:
        model = IndberetningLinje
        fields = (
            "produkttype",
            "produktvægt",
            "levende_vægt",
            "salgspris",
            "fartøj_navn",
            "indhandlingssted",
            "kommentar",
        )

    @property
    def is_negative(self):
        return (
            self.is_bound
            and self.cleaned_data
            and any(
                [
                    True
                    for field in [
                        "produktvægt",
                        "levende_vægt",
                        "salgspris",
                        "transporttillæg",
                        "bonus",
                    ]
                    if self.cleaned_data[field] is not None
                    and self.cleaned_data[field] < 0
                ]
            )
        )


class NonPelagiskPrisRequired:
    def clean(self):
        cleaned_data = super().clean()
        produkttype = cleaned_data.get("produkttype")
        if produkttype and not produkttype.fiskeart.pelagisk:
            for field in self.required_for_pelagisk:
                if cleaned_data.get(field) is None:
                    raise ValidationError(
                        {field: self.fields[field].error_messages["required"]},
                        code="required",
                    )
        return cleaned_data


class IndberetningBaseFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        errors = []
        for function in (
            self.validate_stedkode,
            self.validate_sum_positive,
            self.validate_compartmentalized_sums,
        ):
            try:
                function()
            except ValidationError as e:
                errors.append(e)
        if errors:
            raise ValidationError(errors)

    def get_existing_data(
        self, fields, qs=None, only_negative=False, only_positive=False
    ):
        if self.instance is None:
            return []
        if qs is None:
            qs = self.instance.linjer.all()
        return [
            {field: getattr(linje, field) for field in fields if hasattr(linje, field)}
            for linje in qs
            if (not only_negative or linje.is_negative)
            and (not only_positive or not linje.is_negative)
        ]

    def get_form_data(
        self, fields, default=None, only_negative=False, only_positive=False
    ):
        return [
            {field: form.cleaned_data.get(field) or default for field in fields}
            for form in self.forms
            if (not only_negative or form.is_negative)
            and (not only_positive or not form.is_negative)
        ]

    def validate_stedkode(self):
        fields = (
            "fartøj_navn",
            "indhandlingssted",
            "produkttype",
        )
        existing_data = self.get_existing_data(
            fields, only_positive=True
        ) + self.get_form_data(fields, only_positive=True)
        new_data = self.get_form_data(fields, only_negative=True)
        for data in new_data:
            if data not in existing_data:
                    raise ValidationError(
                        _(
                            "Negative indberetningslinjer skal have fartøjsnavn, indhandlingssted "
                            "og produkttype der matcher med en positiv indberetningslinje"
                        )
                    )

    def validate_sum_positive(self):
        fields = (
            "produktvægt",
            "levende_vægt",
            "salgspris",
            "transporttillæg",
            "bonus",
        )
        data = self.get_existing_data(fields) + self.get_form_data(fields, 0)
        sums = {field: sum([d.get(field) or 0 for d in data]) for field in fields}
        for field in fields:
            if sums[field] < 0:
                raise ValidationError(
                    _(
                        "Summen af tal i hvert felt i indberetningen må ikke være "
                        "i minus, dvs. indberetningen som helhed må kun have en "
                        "positiv sum eller nulstilling."
                    )
                )

    def validate_compartmentalized_sums(self):
        id_fields = (
            "fartøj_navn",
            "indhandlingssted",
            "produkttype",
        )
        amount_fields = (
            "produktvægt",
            "levende_vægt",
            "salgspris",
            "transporttillæg",
            "bonus",
        )
        items = []
        input_data = self.get_existing_data(
            id_fields + amount_fields
        ) + self.get_form_data(id_fields + amount_fields)

        for data in input_data:
            found_item = None
            for item in items:
                if all([item[field] == data.get(field, None) for field in id_fields]):
                    found_item = item
            if found_item is None:
                found_item = {field: data.get(field, None) for field in id_fields}
                found_item.update({field: 0 for field in amount_fields})
                items.append(found_item)
            for field in amount_fields:
                found_item[field] += data.get(field) or 0

        for item in items:
            for field in amount_fields:
                if item[field] < 0:
                    raise ValidationError(
                        _(
                            "Summen af tal i hvert felt i indberetningen for en "
                            "indhandling/fartøj/produkttype må ikke være negativ. "
                            "Summen af feltet %(field)s for %(item)s er negativt",
                        ),
                        params={
                            "field": field.replace("_", " "),
                            "item": ", ".join(
                                [
                                    str(item[field])
                                    for field in id_fields
                                    if item[field] is not None
                                ]
                            ),
                        },
                    )


class IndberetningsLinjeSkema1Form(NonPelagiskPrisRequired, IndberetningsLinjeForm):
    produkttype = ModelChoiceField(
        queryset=ProduktType.objects.filter(
            fiskeart__skematype=1, subtyper=None
        ).order_by("fiskeart__pelagisk", "navn_dk"),
        required=True,
    )
    produktvægt = LocalizedDecimalField(
        required=True,
        clientside_formatting=True,
        max_value=999_999_999,
        min_value=-999_999_999,
    )
    fartøj_navn = CharField(
        widget=Select(
            attrs={
                "class": "js-boat-select form-control col-2 ",
                "autocomplete": "off",
                "style": "width:100%",
            }
        )
    )
    kommentar = CharField(
        widget=Textarea(attrs={"class": "single-line form-control"}), required=False
    )

    required_for_pelagisk = ("salgspris", "transporttillæg")

    class Meta:
        model = IndberetningLinje
        fields = (
            "produkttype",
            "produktvægt",
            "levende_vægt",
            "salgspris",
            "fartøj_navn",
            "transporttillæg",
            "kommentar",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sortér produkttyper i grupper
        self.fields["produkttype"].choices = [
            ("", self.fields["produkttype"].empty_label)
        ] + ProduktType.sort_in_groups(self.fields["produkttype"].queryset)


class IndberetningsLinjeSkema2Form(NonPelagiskPrisRequired, IndberetningsLinjeForm):
    produkttype = ModelChoiceField(
        queryset=ProduktType.objects.filter(
            fiskeart__skematype=2, gruppe=None
        ).order_by("fiskeart__pelagisk", "navn_dk"),
        required=True,
    )
    bonus = LocalizedDecimalField(
        required=True,
        clientside_formatting=True,
        max_value=999_999_999,
        min_value=-999_999_999,
    )
    produktvægt = LocalizedDecimalField(
        required=True,
        clientside_formatting=True,
        max_value=999_999_999,
        min_value=-999_999_999,
    )
    fartøj_navn = CharField(
        widget=Select(
            attrs={
                "class": "js-boat-select form-control col-2",
                "autocomplete": "off",
                "style": "width:100%",
            }
        )
    )
    indhandlingssted = ModelChoiceField(
        queryset=Indhandlingssted.objects.filter(aktiv_til_indhandling=True)
    )
    kommentar = CharField(
        widget=Textarea(attrs={"class": "single-line form-control"}), required=False
    )

    required_for_pelagisk = ("salgspris",)

    class Meta:
        model = IndberetningLinje
        fields = (
            "produkttype",
            "produktvægt",
            "levende_vægt",
            "salgspris",
            "fartøj_navn",
            "indhandlingssted",
            "bonus",
            "kommentar",
        )


class IndberetningsLinjeSkema3Form(IndberetningsLinjeForm):
    produkttype = ModelChoiceField(
        queryset=ProduktType.objects.filter(
            fiskeart__skematype=3, gruppe=None
        ).order_by("fiskeart__pelagisk", "navn_dk"),
        required=True,
    )
    bonus = LocalizedDecimalField(
        required=True,
        clientside_formatting=True,
        max_value=999_999_999,
        min_value=-999_999_999,
    )
    indhandlingssted = ModelChoiceField(
        queryset=Indhandlingssted.objects.filter(aktiv_til_indhandling=True)
    )
    kommentar = CharField(
        widget=Textarea(attrs={"class": "single-line form-control"}), required=False
    )

    class Meta:
        model = IndberetningLinje
        fields = (
            "produkttype",
            "levende_vægt",
            "salgspris",
            "indhandlingssted",
            "bonus",
            "kommentar",
        )


class BilagsForm(ModelForm):
    model = Bilag
    bilag = FileField(widget=FileInput(attrs={"class": "input-file"}))


BilagsFormSet = modelformset_factory(
    Bilag, form=BilagsForm, can_order=False, exclude=("uuid", "indberetning"), extra=1
)


class IndberetningBeregningForm(ModelForm):
    class Meta:
        model = Indberetning
        fields = (
            "afgiftsperiode",
            "skematype",
        )


class IndberetningSearchForm(BootstrapForm):
    afgiftsperiode = ModelChoiceField(
        Afgiftsperiode.objects, required=False, empty_label=_("Alle perioder")
    )
