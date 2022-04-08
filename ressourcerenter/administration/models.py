import logging
from datetime import date
from decimal import Decimal, ROUND_HALF_EVEN
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.utils import timezone
from django.utils.translation import gettext as _, get_language
from io import StringIO
from itertools import chain
from math import ceil
from project.dateutil import quarter_number, month_last_date, quarter_last_month
from simple_history.models import HistoricalRecords
from tenQ.client import put_file_in_prisme_folder, ClientException
from tenQ.writer import G69TransactionWriter
from tenQ.writer import TenQTransactionWriter
from uuid import uuid4
from django.db.models import Max

logger = logging.getLogger(__name__)


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
    history = HistoricalRecords()
    kode = models.PositiveSmallIntegerField(null=True, validators=[MaxValueValidator(999)])

    @staticmethod
    def create_satstabelelementer(sender, instance, **kwargs):
        # Hvis fiskearten har opdateret f.eks. skematyper, kan det være relevant at oprette satstabelementer
        for produkttype in instance.produkttype_set.all():
            for periode in Afgiftsperiode.objects.all():
                for skematype in instance.skematype.all():
                    SatsTabelElement.objects.get_or_create(
                        skematype=skematype,
                        fiskeart=instance,
                        periode=periode,
                        fartoej_groenlandsk=produkttype.fartoej_groenlandsk
                    )

    @staticmethod
    def increment_fiskeart_kode(sender, instance, **kwargs):
        if instance.kode is None:
            current_max = FiskeArt.objects.aggregate(Max('kode'))['kode__max'] or 0
            instance.kode = current_max + 1


m2m_changed.connect(FiskeArt.create_satstabelelementer, FiskeArt.skematype.through, dispatch_uid='create_satstabel_for_fiskeart_m2m')
pre_save.connect(FiskeArt.increment_fiskeart_kode, FiskeArt, dispatch_uid='set_kode_for_fiskeart')


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

    # Eksplicit fangsttype. Hvis null, brug skematypen
    # Det vi normalt kun være rejer der bruger dette felt
    fangsttype = models.CharField(
        null=True,
        default=None,
        max_length=11,
        choices=((x, x) for x in ('havgående', 'indhandling', 'kystnært', 'svalbard')),
    )
    aktivitetskode_indhandling = models.PositiveIntegerField(
        null=True,
        validators=[MaxValueValidator(999999)]
    )
    aktivitetskode_havgående = models.PositiveIntegerField(
        null=True,
        validators=[MaxValueValidator(999999)]
    )
    aktivitetskode_kystnært = models.PositiveIntegerField(
        null=True,
        validators=[MaxValueValidator(999999)]
    )
    aktivitetskode_svalbard = models.PositiveIntegerField(
        null=True,
        validators=[MaxValueValidator(999999)]
    )

    def get_aktivitetskode(self, fangsttype):
        if fangsttype == 'havgående':
            kode = self.aktivitetskode_havgående
        elif fangsttype == 'indhandling':
            kode = self.aktivitetskode_indhandling
        elif fangsttype == 'kystnært':
            kode = self.aktivitetskode_kystnært
        elif fangsttype == 'svalbard':
            kode = self.aktivitetskode_svalbard
        else:
            kode = None
        if kode is None and self.gruppe is not None:
            return self.gruppe.get_aktivitetskode(fangsttype)
        return kode

    history = HistoricalRecords()

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

    @staticmethod
    def create_satstabelelementer(sender, instance, created, raw, using, update_fields, **kwargs):
        # Opret de relevante satstabelelementer for produkttypen på alle perioder. Eksisterende elementer overskrives ikke
        fiskeart = instance.fiskeart
        for periode in Afgiftsperiode.objects.all():
            for skematype in fiskeart.skematype.all():
                SatsTabelElement.objects.get_or_create(
                    skematype=skematype,
                    fiskeart=fiskeart,
                    periode=periode,
                    fartoej_groenlandsk=instance.fartoej_groenlandsk,
                )


post_save.connect(ProduktType.create_satstabelelementer, ProduktType, dispatch_uid='create_satstabel_for_produkttype')


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

    g69transactionwriter = G69TransactionWriter(registreringssted=0, organisationsenhed=0)

    def get_prisme10Q_content(self, max_entries=None, fakturaer=None):
        if fakturaer is None:
            fakturaer = self.fakturaer.filter(bogført__isnull=True)
        if max_entries is not None:
            fakturaer = fakturaer[:max_entries]
        return '\r\n'.join([faktura.prisme10Q_content for faktura in fakturaer])

    def get_prismeG69_content(self, max_entries=None, fakturaer=None):
        if fakturaer is None:
            fakturaer = self.fakturaer.filter(bogført__isnull=True)
        if max_entries is not None:
            fakturaer = fakturaer[:max_entries]
        return '\r\n'.join([faktura.prismeG69_content(self.g69transactionwriter) for faktura in fakturaer])

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
        '10q_development': None
    }

    def send(self, user, force_send_to_test=False, callback=None):
        try:
            if settings.PRISME_PUSH['mock']:
                destinations_available = {'10q_production': False, '10q_development': True}
            else:
                destinations_available = settings.PRISME_PUSH['destinations_available']
            # Send to prod if it is available, fall back to dev
            destination = '10q_production' \
                if destinations_available['10q_production'] and not force_send_to_test else \
                '10q_development'

            self.fejlbesked = ''
            # Extra check for chosen destination
            available = {destination_id for destination_id, label in list(Prisme10QBatch.destinations_available)}
            if destination not in available:
                available_csep = ', '.join(available)
                raise ValueError(f"Kan ikke sende batch til {destination}, det er kun {available_csep} der er tilgængelig på dette system")

            fakturaer = self.fakturaer.filter(bogført__isnull=True)

            destination_folder = settings.PRISME_PUSH['dirs'][destination]
            # When sending to development environment, only send 100 entries
            max_entries = 100 if destination == '10q_development' else None

            content_10q = self.get_prisme10Q_content(max_entries=max_entries, fakturaer=fakturaer)
            content_g69 = self.get_prismeG69_content(max_entries=max_entries, fakturaer=fakturaer)

            if settings.PRISME_PUSH['mock']:
                # Debugging on local environment, output contents to stdout
                logger.info(f"10Q data som ville blive sendt til {destination}: \n------------\n{content_10q}\n------------")
                logger.info(f"G69 data som ville blive sendt til {destination}: \n------------\n{content_g69}\n------------")
            else:
                connection_settings = {
                    'host': settings.PRISME_PUSH['host'],
                    'port': settings.PRISME_PUSH['port'],
                    'username': settings.PRISME_PUSH['username'],
                    'password': settings.PRISME_PUSH['password'],
                    'known_hosts': settings.PRISME_PUSH['known_hosts'],
                }
                filename_10q = "KAS_10Q_export_{}.10q".format(timezone.now().strftime('%Y-%m-%dT%H-%M-%S'))
                filename_g69 = "KAS_G69_export_{}.g69".format(timezone.now().strftime('%Y-%m-%dT%H-%M-%S'))
                put_file_in_prisme_folder(connection_settings, StringIO(content_10q), destination_folder, filename_10q)
                put_file_in_prisme_folder(connection_settings, StringIO(content_g69), destination_folder, filename_g69)
                self.leveret_af = user
                self.leveret_tidspunkt = timezone.now()

            if Prisme10QBatch.completion_statuses[destination]:
                self.status = Prisme10QBatch.completion_statuses[destination]
        except ClientException as e:
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

    opkrævningsdato = models.DateField(
        null=True
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
        if settings.PRISME_PUSH['mock']:
            static_data = {
                'project_id': 'ALIS',
                'user_number': 0,
                'payment_type': 0,
            }
        else:
            static_data = settings.PRISME_PUSH['fielddata']
        return TenQTransactionWriter(
            due_date=self.betalingsdato,
            last_payment_date=self.betalingsdato,
            creation_date=self.linje.indberetningstidspunkt,
            year=self.periode.dato_fra.year,  # Bruges i paalign_aar,
            periode_fra=self.periode.dato_fra,
            periode_til=self.periode.dato_til,
            faktura_no=self.id,
            leverandoer_ident=static_data['project_id'],
            bruger_nummer=static_data['user_number'],
            betal_art=static_data['payment_type'],
            opkraev_date=self.opkrævningsdato or self.betalingsdato,
        ).serialize_transaction(
            cpr_nummer=self.virksomhed.cvr,
            amount_in_dkk=self.beløb,
            afstem_noegle=str(self.pk),
            rate_text=self.text,
            rate_nummer=self.periode.kvartal_nummer,
        )

    def prismeG69_content(self, writer):
        # Writer indeholder en tilstand som opdateres når Fakturaer udskrives. Basically en counter
        linje = self.linje
        if settings.PRISME_PUSH['mock']:
            static_data = {
                'project_id': 'ALIS',
                'user_number': 0,
                'payment_type': 0,
                'account_number': 0,
            }
        else:
            static_data = settings.PRISME_PUSH['fielddata']
        tidtekst = _('{kvartal}. kvartal').format(kvartal=linje.indberetning.afgiftsperiode.kvartal_nummer)
        tekst = ', '.join(filter(None, [
            str(linje.produkttype.fiskeart),
            str(linje.indhandlingssted) if linje.indhandlingssted else None,
            tidtekst
        ]))
        # den dato rederiet indberetter i web-siden for 1, 2, 3 kvartal,
        # hvis det er 4 kvartal, så skal dato være 31.12.2022
        posteringsdato = self.opkrævningsdato or self.betalingsdato

        return writer.serialize_transaction_pair(
            maskinnr=int(static_data['user_number']),
            eks_løbenr=self.id,
            post_dato=posteringsdato,
            kontonr=int(static_data['account_number']),
            beløb=self.beløb,
            is_cvr=True,
            ydelse_modtager=int(linje.indberetning.virksomhed.cvr),
            posteringstekst=tekst[:35],
            ekstern_reference=str(self.id),
        )

    @property
    def text(self):
        # Type afgift og hvilke kvartal, hvis det er indhandling, så skal der stå indhandlingssted og rederiets navn (60 tegn pr. linje)
        textparts = ['Ressourcerenter', str(self.periode), f'({self.linje.produkttype})']
        if self.linje.indhandlingssted:
            textparts.append(str(self.linje.indhandlingssted))

        # Split all parts so they're each <= 60 chars
        splitted_textparts = [x for part in textparts for x in self._split(part)]

        lines = ['']
        for part in splitted_textparts:
            last_line = lines[-1]
            # Each part is known to be less than 60 chars, so append them to lines until a line reaches 60 chars
            if len(last_line) + 1 + len(part) > 60:
                # last_line + ' ' + part will be longer than 60, put part on new line
                lines.append(part)
            else:
                if last_line != '':
                    lines[-1] += ' '  # Add space if not the first word in line
                lines[-1] += part
        return '\r\n'.join(lines)

    # Split a text into chunks with max length 60
    # first split by words, and if any words are longer, split them too
    def _split(self, text):
        if len(text) <= 60:
            return [text]
        if ' ' in text:
            return chain(*[self._split(p) for p in text.split(' ')])
        halfpoint = int(len(text) / 2)
        return chain(self._split(text[0:halfpoint]), self._split(text[halfpoint:]))

    def __str__(self):
        return f"Faktura (kode={self.kode}, periode={self.periode}, beløb={self.beløb})"

    @staticmethod
    def get_betalingsdato(dato):
        # find slutningen af måneden efter kvartalet
        # month_last_date wrapper måneder, så 2022, 13 bliver til 2023, 1
        return month_last_date(dato.year, quarter_last_month(quarter_number(dato)) + 1)

    @staticmethod
    def get_opkrævningsdato(dato):
        # sæt til 31.12 hvis dato ligger i sidste kvartal
        if dato.month >= 10:
            return date(dato.year, 12, 31)
        return dato


class G69Code(models.Model):
    år = models.PositiveSmallIntegerField(
        null=False
    )
    produkttype = models.ForeignKey(
        ProduktType,
        null=False,
        on_delete=models.PROTECT,
    )
    sted = models.ForeignKey(
        'indberetning.Indhandlingssted',
        null=False,
        on_delete=models.PROTECT,
    )
    fangsttype = models.CharField(
        null=False,
        default='indhandling',
        max_length=11,
        choices=((x, x) for x in ('havgående', 'indhandling', 'kystnært', 'svalbard')),
    )
    kode = models.CharField(
        max_length=15
    )

    class Meta:
        unique_together = ['år', 'produkttype', 'sted', 'fangsttype']

    def update_kode(self):
        self.kode = (''.join([
            str(self.år).zfill(2)[-2:],
            str(self.sted.stedkode).zfill(4),
            str(self.produkttype.fiskeart.kode).zfill(2),
            str(self.produkttype.get_aktivitetskode(self.fangsttype)).zfill(6),
        ])).zfill(15)

    @staticmethod
    def update_kode_signal(sender, instance, **kwargs):
        instance.update_kode()

    @staticmethod
    def find_by_indberetningslinje(indberetningslinje):
        sted = indberetningslinje.indhandlingssted
        if sted is None:
            sted = indberetningslinje.indberetning.virksomhed.sted  # TODO: find ud fra CVR
        return G69Code.objects.get(
            år=indberetningslinje.indberetningstidspunkt.year,
            produkttype=indberetningslinje.produkttype,
            sted=sted,
            fangsttype=indberetningslinje.fangsttype,
        )


pre_save.connect(G69Code.update_kode_signal, G69Code, dispatch_uid='G69_update_kode_signal')
