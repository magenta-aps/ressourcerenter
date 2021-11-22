from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from uuid import uuid4
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Iterable


class Kategori(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField(unique=True)  # Hel fisk, filet, bi-produkt
    beskrivelse = models.TextField()


class Kvartal(models.Model):

    class Meta:
        ordering = ['aar', 'kvartal']

    # Oversæt alle feltnavne til dansk
    aar = models.PositiveSmallIntegerField(
        db_index=True,
        verbose_name=_('År'),
        help_text=_('År'),
        null=False,
        blank=False,
    )

    kvartal = models.PositiveSmallIntegerField(
        db_index=True,
        verbose_name=_('Kvartal'),
        help_text=_('Kvartal'),
        null=False,
        blank=False,
        validators=(
            MinValueValidator(limit_value=1),
            MaxValueValidator(limit_value=4),
        )
    )

    # TODO: Behold eller fjern
    dato_fra = models.DateField(null=True)
    dato_til = models.DateField(null=True)

    def __str__(self):
        return f"{self.aar}-{self.kvartal}"


class NamedModel(models.Model):

    class Meta:
        abstract = True

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4
    )
    navn = models.TextField(
        max_length=2048
    )
    beskrivelse = models.TextField(
        blank=True,
        default=""
    )

    def __str__(self):
        return f"{self.navn}"


class FiskeArt(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField(unique=True)
    beskrivelse = models.TextField()

    def __str__(self):
        return self.navn


class FangstType(NamedModel):
    pass


class Ressource(models.Model):

    fiskeart = models.ForeignKey(
        FiskeArt,
        on_delete=models.CASCADE,
        null=False
    )

    fangsttype = models.ForeignKey(
        FangstType,
        on_delete=models.CASCADE,
        null=False
    )


class Afgiftsperiode(models.Model):

    class Meta:
        ordering = ['aarkvartal__aar', 'aarkvartal__kvartal']

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4
    )

    navn = models.TextField(
        default=''
    )

    vis_i_indberetning = models.BooleanField(
        default=False
    )

    aarkvartal = models.ForeignKey(
        Kvartal,
        on_delete=models.CASCADE
    )

    def entry_for_resource(self, ressource):
        try:
            return self.entries.get(ressource=ressource)
        except SatsTabelElement.DoesNotExist:
            return None

    def __str__(self):
        return self.navn


class SatsTabelElement(models.Model):

    tabel = models.ForeignKey(
        Afgiftsperiode,
        on_delete=models.CASCADE,
        related_name='entries'
    )

    ressource = models.ForeignKey(
        Ressource,
        on_delete=models.CASCADE
    )

    rate_pr_kg_indhandling = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    rate_pr_kg_export = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    rate_procent_indhandling = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    rate_procent_export = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    rate_prkg_groenland = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )

    rate_prkg_udenlandsk = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
    )


# Midlertidig
class Fangst(models.Model):

    ressource = models.ForeignKey(
        Ressource,
        on_delete=models.CASCADE
    )

    pris = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default='0.0'
    )

    vaegt = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default='0.0'
    )

    fartoej_groenlandsk = models.BooleanField(
        default=True
    )

    til_export = models.BooleanField(
        default=True
    )

    overfoert_til_tredje_part = models.BooleanField(
        default=False
    )

    export_inkluderet_i_pris = models.BooleanField(
        default=True
    )


class FangstAfgift(models.Model):

    emne = models.ForeignKey(
        Fangst,
        on_delete=models.CASCADE,
        null=False,
    )

    afgift = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default='0.0',
    )

    beregnings_model_indholds_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True
    )  # Model class of the source
    beregnings_model_id = models.PositiveIntegerField(
        null=True
    )  # id of the sources
    beregnings_model = GenericForeignKey(
        'beregnings_model_indholds_type',
        'beregnings_model_id'
    )  # FK to the object who created the transaction

    rate_element = models.ForeignKey(
        SatsTabelElement,
        on_delete=models.SET_NULL,
        null=True,
    )


class BeregningsModel(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(
        max_length=256,
        blank=False,
        null=False,
    )

    def calculate(self, rate_tabel: Afgiftsperiode, dataset: Iterable[Fangst]):
        raise NotImplementedError(f"{self.__class__.__name__}.calculate")


class BeregningsModel2021(BeregningsModel):

    transport_afgift_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_('Transportafgift i procent'),
        null=True,
        default=None
    )

    def calculate(self, rate_tabel: Afgiftsperiode, dataset: Iterable[Fangst]):
        afgift_items = []
        for item in dataset:
            itemdata = model_to_dict(item)
            afgift_item = FangstAfgift()
            self.calculate_transport(itemdata, afgift_item)
            table_entry = rate_tabel.entry_for_resource(itemdata['ressource'])
            if table_entry:
                self.calculate_sats(table_entry, itemdata, afgift_item)
            afgift_items.append(afgift_item)
        return afgift_items

    # 5.2 Når der eksporteres, og udgift til transport ikke er inkluderet, tillæg 1 kr pr kg i handelspris
    def calculate_transport(self, itemdata, afgift_item):
        if itemdata['til_export'] and not itemdata['export_inkluderet_i_pris']:
            itemdata['pris'] += Decimal(1 * itemdata['vaegt'])

    def calculate_sats(self, tabel_entry, itemdata, afgift_item):
        if itemdata['overfoert_til_tredje_part'] or itemdata['til_export']:
            # Afhængigt af table_entry vil flere af disse være 0
            rate_procent = tabel_entry.rate_procent_export or 0
            rate_pr_kg = tabel_entry.rate_pr_kg_export or 0
        else:
            rate_procent = tabel_entry.rate_procent_indhandling or 0
            rate_pr_kg = tabel_entry.rate_pr_kg_indhandling or 0
        if itemdata['fartoej_groenlandsk']:
            rate_pr_kg_2 = tabel_entry.rate_prkg_groenland or 0
        else:
            rate_pr_kg_2 = tabel_entry.rate_prkg_udenlandsk or 0
        # Hvis table_entry er korrekt konstrueret, vil kun ét af disse led være != 0
        afgift = (rate_pr_kg * itemdata['vaegt']) + (rate_pr_kg_2 * itemdata['vaegt']) + (rate_procent * Decimal(0.01) * itemdata['pris'])
        afgift_item.afgift = afgift.quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)
        afgift_item.calculation_model = self
        afgift_item.rate_element = tabel_entry
