from decimal import Decimal, ROUND_HALF_EVEN
from uuid import uuid4

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import gettext as _, get_language

from simple_history.models import HistoricalRecords


class NamedModel(models.Model):

    class Meta:
        abstract = True

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4
    )
    navn_dk = models.TextField(
        max_length=2048,
        verbose_name=_('Dansk navn'),
    )
    navn_gl = models.TextField(
        max_length=2048,
        verbose_name=_('Grønlandsk navn'),
    )
    beskrivelse = models.TextField(
        blank=True,
        default="",
        verbose_name=_('Beskrivelse'),
    )

    def __str__(self):
        if get_language() == 'kl-GL':
            return self.navn_gl
        else:
            return self.navn_dk


class SkemaType(models.Model):

    class Meta:
        ordering = ['id']

    id = models.SmallIntegerField(
        primary_key=True
    )
    navn_dk = models.TextField(
        max_length=2048,
        verbose_name=_('Dansk navn'),
    )
    navn_gl = models.TextField(
        max_length=2048,
        verbose_name=_('Grønlandsk navn'),
    )

    def __str__(self):
        return self.navn_dk


class FiskeArt(NamedModel):

    class Meta:
        ordering = ['navn_dk']

    pelagisk = models.BooleanField(default=False)
    skematype = models.ManyToManyField(SkemaType)
    history = HistoricalRecords()


class ProduktType(NamedModel):

    class Meta:
        unique_together = ['fiskeart', 'navn_dk', 'fartoej_groenlandsk']
        ordering = ('navn_dk',)

    fiskeart = models.ForeignKey(
        FiskeArt,
        on_delete=models.CASCADE,
        null=False
    )

    fartoej_groenlandsk = models.BooleanField(
        null=True
    )


class Afgiftsperiode(NamedModel):

    class Meta:
        ordering = ['-dato_fra', '-dato_til']

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid4
    )

    vis_i_indberetning = models.BooleanField(
        default=False
    )

    dato_fra = models.DateField()

    dato_til = models.DateField()

    history = HistoricalRecords()

    beregningsmodel = models.ForeignKey(
        'BeregningsModel',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )

    def entry_for_resource(self, fiskeart, fangsttype):
        try:
            return self.entries.get(ressource__fiskeart=fiskeart, ressource__fangsttype=fangsttype)
        except SatsTabelElement.DoesNotExist:
            return None


class SatsTabelElement(models.Model):

    class Meta:
        unique_together = ['periode', 'skematype', 'fiskeart', 'fartoej_groenlandsk']

    periode = models.ForeignKey(
        Afgiftsperiode,
        on_delete=models.CASCADE,
        related_name='entries'
    )

    skematype = models.ForeignKey(
        SkemaType,
        on_delete=models.CASCADE
    )

    fiskeart = models.ForeignKey(
        FiskeArt,
        on_delete=models.CASCADE
    )

    fartoej_groenlandsk = models.BooleanField(
        null=True
    )

    def __str__(self):
        return f"{self.fiskeart} | {self.periode}"

    rate_pr_kg = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Afgift, kr/kg'),
    )

    rate_procent = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Afgift, procent af salgspris'),
    )

    history = HistoricalRecords()

    @staticmethod
    def create_for_period_from_resources(sender, instance, created, raw, using, update_fields, **kwargs):
        if created is True:
            for skematype in SkemaType.objects.all():
                for fiskeart in skematype.fiskeart_set.all():
                    for produkttype in fiskeart.produkttype_set.all():
                        SatsTabelElement.objects.create(
                            skematype=skematype,
                            fiskeart=fiskeart,
                            periode=instance,
                            fartoej_groenlandsk=produkttype.fartoej_groenlandsk
                        )


post_save.connect(SatsTabelElement.create_for_period_from_resources, Afgiftsperiode, dispatch_uid='create_satstabel_for_period')


class FangstAfgift(models.Model):

    indberetninglinje = models.OneToOneField(
        'indberetning.IndberetningLinje',
        on_delete=models.CASCADE,
        null=True,
    )

    afgift = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default='0.0',
    )

    beregningsmodel = models.ForeignKey(
        'BeregningsModel',
        on_delete=models.SET_NULL,
        null=True,
        default=None,
    )

    rate_element = models.ForeignKey(
        SatsTabelElement,
        on_delete=models.SET_NULL,
        null=True,
    )

    rate_procent = models.DecimalField(
        null=True,
        max_digits=4,
        decimal_places=2,
    )
    rate_pr_kg = models.DecimalField(
        null=True,
        max_digits=6,
        decimal_places=2,
    )

    def to_json(self):
        return {
            'beregningsmodel': self.beregningsmodel.pk if self.beregningsmodel else None,
            'rate_element': self.rate_element.pk if self.rate_element else None,
            'afgift': str(self.afgift),
            'rate_procent': str(self.rate_procent),
            'rate_pr_kg': str(self.rate_pr_kg)
        }

    def rate_string(self):
        lines = []
        if self.rate_pr_kg:
            lines.append(_('%s kr/kg') % self.rate_pr_kg)
        if self.rate_procent:
            lines.append(_('%s%% af salgspris') % self.rate_procent)
        return '+'.join(lines)


class BeregningsModel(models.Model):

    navn = models.CharField(
        max_length=256,
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self):
        return self.navn

    # BeregningsModel-implementationer kan være et arbitrært hierarki af klasser, f.eks.:
    # class BeregningsModelA(BeregningsModel)
    # class BeregningsModelB(BeregningsModelA)
    # class BeregningsModelC(BeregningsModelB)
    # find den specifikke leaf-instans (instansen af BeregningsModelC som peger på dette objekt)
    @property
    def specific(self):
        instance = self
        while (next := instance.subclass_instance) != instance:
            instance = next
        return instance

    def calculate(self, indberetning):
        return self.specific.calculate(indberetning)

    def calculate_for_linje(self, indberetninglinje):
        return self.specific.calculate_for_linje(indberetninglinje)


class BeregningsModel2021(BeregningsModel):

    beregningsmodel_ptr = models.OneToOneField(
        BeregningsModel,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='subclass_instance',
    )

    transport_afgift_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name=_('Transportafgift i procent'),
        null=True,
        default=None
    )

    def get_satstabelelement(self, indberetninglinje):
        return SatsTabelElement.objects.get(
            periode=indberetninglinje.indberetning.afgiftsperiode,
            skematype=indberetninglinje.indberetning.skematype,
            fiskeart=indberetninglinje.produkttype.fiskeart,
            fartoej_groenlandsk=indberetninglinje.produkttype.fartoej_groenlandsk,
        )

    def calculate(self, indberetning):
        afgift_items = []
        for indberetninglinje in indberetning.linjer.all():
            afgift_items.append(self.calculate_for_linje(indberetninglinje))
        return afgift_items

    def calculate_for_linje(self, indberetninglinje):
        sats = self.get_satstabelelement(indberetninglinje)
        afgift_item = FangstAfgift()

        rate_procent = sats.rate_procent or 0
        rate_pr_kg = sats.rate_pr_kg or 0
        vaegt = indberetninglinje.levende_vægt or 0
        pris = indberetninglinje.salgspris or 0

        # Hvis table_entry er korrekt konstrueret, vil kun ét af disse led være != 0
        afgift = (rate_pr_kg * vaegt) + (rate_procent * Decimal(0.01) * pris)

        afgift_item.afgift = afgift.quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)
        afgift_item.calculation_model = self
        afgift_item.rate_element = sats
        afgift_item.rate_pr_kg = rate_pr_kg
        afgift_item.rate_procent = rate_procent
        afgift_item.indberetninglinje = indberetninglinje
        return afgift_item
