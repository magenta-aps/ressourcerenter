from decimal import Decimal, ROUND_HALF_EVEN
from uuid import uuid4

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext as _

from simple_history.models import HistoricalRecords


class ProduktKategori(models.Model):

    class Meta:
        ordering = ['navn']

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4
    )
    navn = models.TextField(  # Hel fisk, filet, bi-produkt
        unique=True
    )
    beskrivelse = models.TextField(
        null=False,
        blank=True,
        default='',
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.navn


class NamedModel(models.Model):

    class Meta:
        abstract = True

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4
    )
    navn = models.TextField(
        max_length=2048,
        verbose_name=_('Navn'),
    )
    beskrivelse = models.TextField(
        blank=True,
        default="",
        verbose_name=_('Beskrivelse'),
    )

    def __str__(self):
        return f"{self.navn}"


class FiskeArt(models.Model):

    class Meta:
        ordering = ['navn']

    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField(unique=True)
    beskrivelse = models.TextField()
    history = HistoricalRecords()

    def __str__(self):
        return self.navn


class FangstType(NamedModel):
    pass


class Ressource(models.Model):

    class Meta:
        unique_together = ['fiskeart', 'fangsttype']

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

    def __str__(self):
        return f"{self.fiskeart.navn} | {self.fangsttype.navn}"


class Afgiftsperiode(models.Model):

    class Meta:
        ordering = ['dato_fra', 'dato_til']

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

    dato_fra = models.DateField()

    dato_til = models.DateField()

    history = HistoricalRecords()

    def entry_for_resource(self, fiskeart, fangsttype):
        try:
            return self.entries.get(ressource__fiskeart=fiskeart, ressource__fangsttype=fangsttype)
        except SatsTabelElement.DoesNotExist:
            return None

    def __str__(self):
        return self.navn


class SatsTabelElement(models.Model):

    class Meta:
        unique_together = ['periode', 'ressource']

    periode = models.ForeignKey(
        Afgiftsperiode,
        on_delete=models.CASCADE,
        related_name='entries'
    )

    ressource = models.ForeignKey(
        Ressource,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.ressource} | {self.periode.navn}"

    rate_pr_kg_indhandling = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Indhandling, kr/kg'),
    )

    rate_pr_kg_export = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Eksport, kr/kg'),
    )

    rate_procent_indhandling = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Indhandling, procent af salgspris'),
    )

    rate_procent_export = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Eksport, procent af salgspris'),
    )

    rate_prkg_groenland = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Grønlandsk fartøj, kr/kg'),
    )

    rate_prkg_udenlandsk = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Udenlandsk fartøj, kr/kg'),
    )

    history = HistoricalRecords()

    @staticmethod
    def create_for_period_from_resources(sender, instance, created, raw, using, update_fields, **kwargs):
        if created is True:
            for ressource in Ressource.objects.all():
                SatsTabelElement.objects.create(ressource=ressource, periode=instance)


post_save.connect(SatsTabelElement.create_for_period_from_resources, Afgiftsperiode, dispatch_uid='create_satstabel_for_period')


class FangstAfgift(models.Model):

    indberetninglinje = models.ForeignKey(
        'indberetning.IndberetningLinje',
        on_delete=models.CASCADE,
        null=True,
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

    def calculate(self, rate_tabel: Afgiftsperiode, indberetning):
        raise NotImplementedError(f"{self.__class__.__name__}.calculate")


class BeregningsModel2021(BeregningsModel):

    transport_afgift_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_('Transportafgift i procent'),
        null=True,
        default=None
    )

    def calculate(self, rate_tabel: Afgiftsperiode, indberetning, til_export=False, overfoert_til_tredje_part=False, export_inkluderet_i_pris=False, fartoej_groenlandsk=True):
        afgift_items = []

        # TODO: Find ud af fangsttypen fra Indberetningen på en bedre måde.
        fangsttype_navn = 'Havgående' if indberetning.indberetnings_type == 'havgående' else 'Kystnært'
        fangsttype = FangstType.objects.get(navn=fangsttype_navn)

        for indberetninglinje in indberetning.linjer.all():
            afgift_item = FangstAfgift()
            table_entry = rate_tabel.entry_for_resource(indberetninglinje.fiskeart, fangsttype)  # indberetninglinje.kategori
            if table_entry:
                self.calculate_sats(table_entry, indberetninglinje, afgift_item, til_export=til_export, overfoert_til_tredje_part=overfoert_til_tredje_part, export_inkluderet_i_pris=export_inkluderet_i_pris, fartoej_groenlandsk=fartoej_groenlandsk)
            afgift_items.append(afgift_item)
        return afgift_items

    def calculate_sats(self, tabel_entry, indberetninglinje, afgift_item, til_export=False, overfoert_til_tredje_part=False, export_inkluderet_i_pris=False, fartoej_groenlandsk=True):

        if overfoert_til_tredje_part or til_export:
            # Afhængigt af table_entry vil flere af disse være 0
            rate_procent = tabel_entry.rate_procent_export or 0
            rate_pr_kg = tabel_entry.rate_pr_kg_export or 0
        else:
            rate_procent = tabel_entry.rate_procent_indhandling or 0
            rate_pr_kg = tabel_entry.rate_pr_kg_indhandling or 0

        if fartoej_groenlandsk:
            rate_pr_kg_2 = tabel_entry.rate_prkg_groenland or 0
        else:
            rate_pr_kg_2 = tabel_entry.rate_prkg_udenlandsk or 0

        vaegt = indberetninglinje.levende_vægt
        pris = indberetninglinje.salgspris
        if til_export and not export_inkluderet_i_pris:
            pris += Decimal(1 * vaegt)

        # Hvis table_entry er korrekt konstrueret, vil kun ét af disse led være != 0
        afgift = (rate_pr_kg * vaegt) + (rate_pr_kg_2 * vaegt) + (rate_procent * Decimal(0.01) * pris)
        afgift_item.afgift = afgift.quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)

        afgift_item.calculation_model = self
        afgift_item.rate_element = tabel_entry
        return afgift_item
