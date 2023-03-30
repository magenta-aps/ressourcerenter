import logging
import os
from administration.models import SkemaType, Afgiftsperiode, ProduktType
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator
from django.db import models, IntegrityError
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from indberetning.validators import validate_cvr, validate_cpr
from uuid import uuid4

from project.views_mixin import Trunc

logger = logging.getLogger(__name__)


def get_virksomhed_default_sted():
    return Indhandlingssted.objects.get(navn="Nuuk").uuid


class Virksomhed(models.Model):
    class Meta:
        ordering = ["navn"]

    uuid = models.UUIDField(primary_key=True, default=uuid4)
    cvr = models.TextField(
        unique=True,
        validators=[validate_cvr],
        verbose_name=_("CVR-nummer"),
        db_index=True,
    )
    kontakt_person = models.TextField(
        default="", blank=True, verbose_name=_("Kontaktperson navn")
    )
    kontakt_email = models.EmailField(
        default="", blank=True, verbose_name=_("Kontaktperson email")
    )
    kontakts_phone_nr = models.TextField(
        default="", blank=True, verbose_name=_("Kontaktperson telefonnr")
    )
    navn = models.TextField(verbose_name=_("Navn"), null=True)
    sted = models.ForeignKey(
        "Indhandlingssted",
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        default=get_virksomhed_default_sted,
    )

    def __str__(self):
        if self.navn:
            return f"{self.navn} (CVR: {self.cvr})"
        else:
            return f"CVR {self.cvr}"


class Indhandlingssted(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField(null=False, unique=True)
    stedkode = models.PositiveIntegerField(
        validators=[MaxValueValidator(999999)], unique=True
    )
    aktiv_til_indhandling = models.BooleanField(default=True)

    def __str__(self):
        return self.navn

    class Meta:
        ordering = ("navn",)

    @property
    def stedkode_str(self):
        return str(self.stedkode).zfill(6)


navne_typer = (("fartøj", _("Fartøj")), ("indhandlings_sted", _("Indhandlingssted")))


class Navne(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField()  # Fartoejs navn, bygd, indhandlingsted
    virksomhed = models.ForeignKey(Virksomhed, on_delete=models.CASCADE)
    type = models.TextField(choices=navne_typer)

    def __str__(self):
        return self.navn

    class Meta:
        unique_together = ("navn", "virksomhed", "type")


class Indberetning(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    skematype = models.ForeignKey(SkemaType, on_delete=models.CASCADE)
    virksomhed = models.ForeignKey(Virksomhed, on_delete=models.PROTECT)
    indberetters_cpr = models.TextField(
        validators=[validate_cpr]
    )  # CPR fra medarbejdersignatur eller mitid
    administrator = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.PROTECT
    )  # only used when sudo is used
    afgiftsperiode = models.ForeignKey(Afgiftsperiode, on_delete=models.PROTECT)
    indberetningstidspunkt = models.DateTimeField(auto_now_add=True, db_index=True)
    afstemt = models.BooleanField(default=False)

    def get_fishcategories_string(self):
        fishtypes = {
            str(linje.produkttype.fiskeart): None for linje in self.linjer.all()
        }
        return "; ".join(fishtypes.keys())

    def get_first_comment_string(self):
        linje = self.linjer.exclude(kommentar="")
        if linje:
            return linje.kommentar

    def get_all_comment_strings(self):
        return [linje.kommentar for linje in self.linjer.exclude(kommentar="")]

    def get_first_comment(self):
        for linje in self.linjer.all():
            if linje.kommentar != "":
                return linje.kommentar
        return ""

    @property
    def afgift_sum(self):
        return self.linjer.aggregate(sum=Sum("fangstafgift__afgift"))["sum"]
        # return sum([linje.fangstafgift.afgift for linje in self.linjer.all()])

    @property
    def afgift_sum_afrundet(self):
        return self.linjer.aggregate(sum=Trunc(Sum("fangstafgift__afgift")))["sum"]

    def to_json(self):
        return {
            "skematype.id": self.skematype.id,
            "virksomhed.cvr": self.virksomhed.cvr,
            "indberetters_cpr": self.indberetters_cpr,
            "administrator.id": self.administrator.id if self.administrator else None,
            "afgiftsperiode.uuid": self.afgiftsperiode.uuid,
        }

    class Meta:
        ordering = ("indberetningstidspunkt",)


class IndberetningLinje(models.Model):
    # eksport: summer på kategori niveau
    # indhandling: summer på fiskearts niveau
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    fartøj_navn = models.TextField(null=True)
    indhandlingssted = models.ForeignKey(
        Indhandlingssted, null=True, on_delete=models.SET_NULL
    )
    indberetning = models.ForeignKey(
        Indberetning, on_delete=models.CASCADE, related_name="linjer"
    )
    produkttype = models.ForeignKey(ProduktType, on_delete=models.PROTECT)

    produktvægt = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, verbose_name=_("Produktvægt (kg)")
    )
    levende_vægt = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        verbose_name=_("Levende vægt/helfisk mængde (kg)"),
    )  # hel fisk
    salgspris = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, verbose_name=_("Salgspris (kr)")
    )
    transporttillæg = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Transporttillæg (kr)"),
    )
    bonus = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Bonus og andet vederlag (kr)"),
    )
    kommentar = models.TextField(default="", blank=True)

    debitorgruppekode = models.PositiveSmallIntegerField(default=0)

    # Nødvendig for at vi kan tracke linjer der oprettes senere end indberetningen
    indberetningstidspunkt = models.DateTimeField(auto_now_add=True, db_index=True)

    faktura = models.OneToOneField(
        "administration.Faktura",
        null=True,
        on_delete=models.SET_NULL,
        related_name="linje",
    )

    @property
    def afgift(self):
        return self.fangstafgift.afgift

    def calculate_afgift(self):
        afgiftsperiode = self.indberetning.afgiftsperiode
        beregningsmodel = afgiftsperiode.beregningsmodel
        if beregningsmodel is None:
            raise Exception(
                f"Kan ikke beregne afgift for Indberetningslinje; beregningsmodel er ikke sat for afgiftsperiode {afgiftsperiode}"
            )
        return beregningsmodel.calculate_for_linje(self)

    @property
    def fangsttype(self):
        # For de fleste fiskearter er fangsttypen (havgående, kystnær, indhandling) dikteret af skematypen
        produkttype = self.produkttype
        while produkttype.gruppe is not None:
            produkttype = produkttype.gruppe

        skematype = self.indberetning.skematype
        if skematype.id == 2:
            # Hvis skematype 2, brug ikke produkttype
            return "indhandling"
        if produkttype.fangsttype:
            # Lad produkttyper som definerer en fangsttype (fx. rejer) overstyre
            return produkttype.fangsttype
        if skematype.id == 1:
            return "havgående"
        if skematype.id == 3:
            return "kystnært"

    @property
    def fangsttype_display(self):
        fangsttype = self.fangsttype
        if fangsttype == "havgående":
            return _("Havgående")
        if fangsttype == "kystnært":
            return _("Kystnært")
        if fangsttype == "indhandling":
            return _("Indhandling")
        if fangsttype == "svalbard":
            return _("Svalbard og Barentshavet")

    def save(self, *args, **kwargs):
        if self.salgspris is not None:
            self.salgspris = round(self.salgspris, 0)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("produkttype__navn_dk",)


@receiver(
    post_save,
    sender=IndberetningLinje,
    dispatch_uid="indberetninglinje_calculate_afgift",
)
def calculate_afgift(sender, **kwargs):
    indberetningslinje = kwargs["instance"]
    try:
        fangstafgift = indberetningslinje.calculate_afgift()
        # Note: koblingen er one-to-one, så hvis man forsøger at oprette en fangstafgift for en indberetningslinje
        # der allerede har én, springer det i luften, men eftersom indberetningslinjer kun skal gemmes én gang
        # bør det være et non-issue.
        fangstafgift.save()
    except Exception as e:
        print(e)


@receiver(post_save, sender=IndberetningLinje, dispatch_uid="indberetning_store_navne")
def store_navne(sender, **kwargs):
    # store new names
    instance = kwargs["instance"]

    for navn, navnetype in (
        (instance.fartøj_navn, "fartøj"),
        (instance.indhandlingssted, "indhandlings_sted"),
    ):
        if navn is not None and navn != "":
            try:
                Navne.objects.get_or_create(
                    virksomhed=instance.indberetning.virksomhed,
                    navn=navn,
                    type=navnetype,
                )
            except IntegrityError:
                # navn already exists
                pass


def bilag_filepath(instance, filename):
    return "bilag/{uuid}/{filename}".format(
        uuid=instance.indberetning.uuid, filename=filename
    )


class Bilag(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    indberetning = models.ForeignKey(
        Indberetning, on_delete=models.PROTECT, related_name="bilag"
    )
    bilag = models.FileField(upload_to=bilag_filepath)

    @property
    def filename(self):
        return os.path.basename(self.bilag.name)
