from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from administration.models import Afgiftsperiode, FiskeArt, Kategori
from uuid import uuid4
from indberetning.validators import validate_cvr, validate_cpr
from django.core.validators import MinValueValidator
from decimal import Decimal


class Virksomhed(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    cvr = models.TextField(unique=True, validators=[validate_cvr])
    kontakt_person = models.TextField(default='', blank=True)
    kontakt_email = models.EmailField(default='', blank=True)
    kontakts_phone_nr = models.TextField(default='', blank=True)


navne_typer = (
    ('fartøj', _('Fartøj')),
    ('indhandlings_sted', _('Indhandlings sted'))
)


class Navne(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField()  # Fartoejs navn, bygd, indhalningsanlæg
    virksomhed = models.ForeignKey(Virksomhed, on_delete=models.CASCADE)
    type = models.TextField(choices=navne_typer)

    class Meta:
        unique_together = ('navn', 'virksomhed')


indberetnings_type_choices = (
    ('havgående', _('Havgående fangst')),
    ('indhandling', _('Indhandling af fangst'))
)


class Indberetning(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    indberetnings_type = models.TextField(choices=indberetnings_type_choices)
    virksomhed = models.ForeignKey(Virksomhed, on_delete=models.PROTECT, db_index=True)
    indberetters_cpr = models.TextField(validators=[validate_cpr])  # CPR fra medarbejder signatur eller nemid
    administrator = models.ForeignKey(get_user_model(), null=True, on_delete=models.PROTECT)  # only used when sudo is used
    afgiftsperiode = models.ForeignKey(Afgiftsperiode, on_delete=models.PROTECT, db_index=True)
    indberetningstidspunkt = models.DateTimeField(auto_now_add=True)
    navn = models.TextField()  # fartojs navn eller indhanlingssted/bygd

    def get_navn_display(self):
        if self.indberetnings_type == 'havgående':
            return _('Fartøjets navn')
        return _('indhandlingssted/Bygd')

    class Meta:
        ordering = ('indberetningstidspunkt', )


class IndberetningLinje(models.Model):
    # eksport: summer på kategori niveau
    # indhandling: summer på fiskearts niveau
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    indberetning = models.ForeignKey(Indberetning, on_delete=models.CASCADE)
    fiskeart = models.ForeignKey(FiskeArt, on_delete=models.PROTECT)
    kategori = models.ForeignKey(Kategori, on_delete=models.PROTECT, null=True, blank=True)  # burges kun til eksport
    salgs_vægt = models.DecimalField(max_digits=20, decimal_places=2,
                                     verbose_name=_('Vægt/Mængde kg'),
                                     validators=[MinValueValidator(Decimal('0.00'))])
    levende_vægt = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True,
                                       verbose_name=_('Levende vægt/helfisk mængde (kg)'),
                                       validators=[MinValueValidator(Decimal('0.00'))])  # hel fisk
    salgs_pris = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True, verbose_name=_('Omsætning'),
                                     validators=[MinValueValidator(Decimal('0.00'))])


def bilag_filepath(instance, filename):
    return 'bilag/{uuid}/{filename}'.format(uuid=instance.indberetning.uuid,
                                            filename=filename)


class Bilag(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    indberetning = models.ForeignKey(Indberetning, on_delete=models.PROTECT)
    bilag = models.FileField()
