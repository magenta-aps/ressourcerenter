import tempfile
from decimal import Decimal, ROUND_HALF_EVEN
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import gettext as _, get_language

from simple_history.models import HistoricalRecords
from tenQ.client import put_file_in_prisme_folder
from tenQ.writer import TenQTransactionWriter
from uuid import uuid4
from math import ceil


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
        if get_language() == 'kl-GL':
            return self.navn_gl
        else:
            return self.navn_dk


class FiskeArt(NamedModel):

    class Meta:
        ordering = ['navn_dk']

    pelagisk = models.BooleanField(default=False)
    skematype = models.ManyToManyField(SkemaType)
    debitorgruppekode_indhandling = models.PositiveSmallIntegerField(validators=[MaxValueValidator(999)], null=True)
    debitorgruppekode_kystnært = models.PositiveSmallIntegerField(validators=[MaxValueValidator(999)], null=True)
    debitorgruppekode_havgående = models.PositiveSmallIntegerField(validators=[MaxValueValidator(999)], null=True)
    history = HistoricalRecords()
    debitorgruppekode_use_skematype = models.BooleanField(default=True)

    def get_fangsttype(self, skematype):
        if self.debitorgruppekode_use_skematype:
            if skematype.id == 1:
                return 'havgående'
            elif skematype.id == 2:
                return 'indhandling'
            elif skematype.id == 3:
                return 'kystnært'
        else:
            if self.debitorgruppekode_indhandling:
                return 'indhandling'
            elif self.debitorgruppekode_kystnært:
                return 'kystnært'
            elif self.debitorgruppekode_havgående:
                return 'havgående'

    def get_debitorgruppekode(self, skematype):
        fangsttype = self.get_fangsttype(skematype)
        if fangsttype == 'havgående':
            return self.debitorgruppekode_havgående
        elif fangsttype == 'indhandling':
            return self.debitorgruppekode_indhandling
        elif fangsttype == 'kystnært':
            return self.debitorgruppekode_kystnært


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
    # Skematype 1's queryset skal være produkter som ikke har children
    # andre skematyper skal være produkter som ikke er children
    gruppe = models.ForeignKey(
        'ProduktType',
        null=True,
        blank=True,
        related_name='subtyper',
        on_delete=models.SET_NULL,
    )

    @staticmethod
    def sort_in_groups(produkttyper):
        groups = {}
        non_group_items = {}
        for item in produkttyper:
            if item.gruppe:
                gruppenavn = str(item.gruppe)
                if gruppenavn not in groups:
                    groups[gruppenavn] = [gruppenavn, []]
                groups[gruppenavn][1].append((str(item.pk), str(item)))
            else:
                non_group_items[str(item)] = (str(item.pk), str(item))
        return [groups[x] for x in sorted(groups)] + [non_group_items[x] for x in sorted(non_group_items)]


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

    @property
    def kvartal_nummer(self):
        return ceil(self.dato_fra.month / 3)


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
                    for valuedict in fiskeart.produkttype_set.values('fartoej_groenlandsk').order_by('fartoej_groenlandsk').distinct('fartoej_groenlandsk'):
                        fartoej_groenlandsk = valuedict['fartoej_groenlandsk']
                        SatsTabelElement.objects.create(
                            skematype=skematype,
                            fiskeart=fiskeart,
                            periode=instance,
                            fartoej_groenlandsk=fartoej_groenlandsk
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
            lines.append(_('%s kr/kg') % str(self.rate_pr_kg).replace('.', ','))
        if self.rate_procent:
            lines.append(_('%s %%') % str(self.rate_procent).replace('.', ','))
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
        try:
            afgift_item = indberetninglinje.fangstafgift
        except ObjectDoesNotExist:
            afgift_item = FangstAfgift()

        rate_procent = sats.rate_procent or 0
        rate_pr_kg = sats.rate_pr_kg or 0
        vaegt = indberetninglinje.levende_vægt or 0
        pris = (indberetninglinje.salgspris or 0)
        if indberetninglinje.transporttillæg:
            pris += indberetninglinje.transporttillæg
        elif indberetninglinje.bonus:
            pris += indberetninglinje.bonus

        # Hvis table_entry er korrekt konstrueret, vil kun ét af disse led være != 0
        afgift = (rate_pr_kg * vaegt) + (rate_procent * Decimal(0.01) * pris)

        afgift_item.afgift = afgift.quantize(Decimal('.01'), rounding=ROUND_HALF_EVEN)
        afgift_item.calculation_model = self
        afgift_item.rate_element = sats
        afgift_item.rate_pr_kg = rate_pr_kg
        afgift_item.rate_procent = rate_procent
        afgift_item.indberetninglinje = indberetninglinje
        return afgift_item


class Prisme10QBatch(models.Model):
    class Meta:
        ordering = ['oprettet_tidspunkt']
        verbose_name = _('prisme 10Q batch')
        verbose_name_plural = _('prisme 10Q batches')

    # When was the batch created
    oprettet_tidspunkt = models.DateTimeField(auto_now=True)
    # Who created the batch
    oprettet_af = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='created_prisme_batches',
    )
    # When was the batch delivered
    leveret_tidspunkt = models.DateTimeField(blank=True, null=True)
    # Who delivered the batch
    leveret_af = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='prisme_batches',
    )
    # Any error encountered while trying to deliver the batch
    fejlbesked = models.TextField(blank=True, default='')

    # Status for delivery
    STATUS_CREATED = 'created'
    STATUS_DELIVERING = 'delivering'
    STATUS_DELIVERY_FAILED = 'failed'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    status_choices = (
        (STATUS_CREATED, _('Ikke afsendt')),
        (STATUS_DELIVERING, _('Afsender')),
        (STATUS_DELIVERY_FAILED, _('Afsendelse fejlet')),
        (STATUS_DELIVERED, _('Afsendt')),
        (STATUS_CANCELLED, _('Annulleret'))
    )

    status = models.CharField(
        choices=status_choices,
        default=STATUS_CREATED,
        max_length=15
    )

    def get_prisme10Q_content(self, max_entries=None):
        qs = self.fakturaer.filter(bogført__isnull=True)
        if max_entries is not None:
            qs = qs[:max_entries]
        return '\r\n'.join([faktura.prisme10Q_content for faktura in qs])

    destinations_all = (
        ('10q_development', _('Undervisningssystem')),
        ('10q_production', _('Produktionssystem')),
    )
    destinations_available = tuple((
        (destination_id, label,)
        for destination_id, label in destinations_all
        if settings.PRISME_PUSH['destinations_available'][destination_id]
    ))
    completion_statuses = {
        '10q_production': STATUS_DELIVERED,
        '10q_development': STATUS_CREATED
    }

    def send(self, destination, user, callback=None):
        try:
            self.fejlbesked = ''
            # Extra check for chosen destination
            b = list(Prisme10QBatch.destinations_available)
            available = {destination_id for destination_id, label in b}
            if destination not in available:
                available_csep = ', '.join(available)
                raise ValueError(f"Kan ikke sende batch til {destination}, det er kun {available_csep} der er tilgængelig på dette system")

            destination_folder = settings.PRISME_PUSH['dirs'][destination]
            # When sending to development environment, only send 100 entries
            content = self.get_prisme10Q_content(100 if destination == '10q_development' else None)
            filename = "KAS_10Q_export_{}.10q".format(timezone.now().strftime('%Y-%m-%dT%H-%M-%S'))
            connection_settings = {
                'host': settings.PRISME_PUSH['host'],
                'port': settings.PRISME_PUSH['port'],
                'username': settings.PRISME_PUSH['username'],
                'password': settings.PRISME_PUSH['password'],
                'known_hosts': settings.PRISME_PUSH['known_hosts'],
            }
            if settings.PRISME_PUSH['do_send']:
                with tempfile.NamedTemporaryFile(mode='w') as batchfile:
                    batchfile.write(content)
                    batchfile.flush()
                    put_file_in_prisme_folder(connection_settings, batchfile.name, destination_folder, filename, callback)
                self.leveret_af = user
                self.leveret_tidspunkt = timezone.now()
            else:
                # Debugging on local environment, output contents to stdout
                print(f"10Q data som ville blive sendt til {destination}: \n------------\n{content}\n------------")

            self.status = Prisme10QBatch.completion_statuses[destination]
        except Exception as e:
            self.status = Prisme10QBatch.STATUS_DELIVERY_FAILED
            self.fejlbesked = str(e)
            raise
        finally:
            self.save()


class Faktura(models.Model):

    virksomhed = models.ForeignKey(
        'indberetning.Virksomhed',
        null=False,
        on_delete=models.CASCADE
    )

    beløb = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.0'),
    )

    betalingsdato = models.DateField(
        null=False
    )

    periode = models.ForeignKey(
        Afgiftsperiode,
        on_delete=models.SET_NULL,
        null=True
    )

    opretter = models.ForeignKey(
        get_user_model(),
        null=False,
        on_delete=models.CASCADE,
    )

    oprettet = models.DateTimeField(
        auto_now_add=True,
        null=False,
    )

    bogført = models.DateField(
        null=True
    )

    kode = models.PositiveSmallIntegerField(
        null=False
    )

    batch = models.ForeignKey(
        Prisme10QBatch,
        null=True,
        on_delete=models.CASCADE,
        related_name='fakturaer',
    )

    @property
    def prisme10Q_content(self):
        static_data = settings.PRISME_PUSH['fielddata']
        return TenQTransactionWriter(
            due_date=self.betalingsdato,
            creation_date=self.linje.indberetningstidspunkt,
            year=self.periode.dato_fra.year,  # Bruges i paalign_aar,
            periode_fra=self.periode.dato_fra,
            periode_til=self.periode.dato_til,
            faktura_no=self.id,
            leverandoer_ident=static_data['project_id'],
            bruger_nummer=static_data['user_number'],
            betal_art=static_data['payment_type'],
        ).serialize_transaction(
            cpr_nummer=self.virksomhed.cvr,
            amount_in_dkk=self.beløb,
            afstem_noegle=str(self.pk),
            rate_text=self.text,
            rate_nummer=self.periode.kvartal_nummer,
        )

    @property
    def text(self):
        # Type afgift og hvilke kvartal, hvis det er indhandling, så skal der stå indhandlingssted og rederiets navn (60 tegn pr. linje)
        textparts = ['Ressourcerenter', str(self.periode), f'({self.linje.produkttype})']
        if self.linje.indhandlingssted:
            textparts.append(str(self.linje.indhandlingssted))
        return ' '.join(textparts)

    def __str__(self):
        return f"Faktura (kode={self.kode}, periode={self.periode}, beløb={self.beløb})"

    @staticmethod
    def from_linje(linje, opretter, betalingsdato, batch=None):
        kode = linje.debitorgruppekode  # Kode er unik for fiskeart/fangststed

        faktura = Faktura.objects.create(
            kode=kode,
            periode=linje.indberetning.afgiftsperiode,
            opretter=opretter,
            virksomhed=linje.indberetning.virksomhed,
            betalingsdato=betalingsdato,
            batch=batch,
            beløb=linje.afgift
        )

        linje.faktura = faktura
        linje.save(update_fields=['faktura'])
        return faktura
