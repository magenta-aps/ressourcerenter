import os
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from administration.models import Afgiftsperiode, FiskeArt, ProduktKategori
from indberetning.validators import validate_cvr, validate_cpr


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
    navn = models.TextField()  # Fartoejs navn, bygd, indhandlingsted
    virksomhed = models.ForeignKey(Virksomhed, on_delete=models.CASCADE)
    type = models.TextField(choices=navne_typer)

    def __str__(self):
        return self.navn

    class Meta:
        unique_together = ('navn', 'virksomhed', 'type')


indberetnings_type_choices = (
    ('fartøj', _('Indrapportering fra fartøj')),
    ('pelagisk', _('Pelagisk fiskeri')),
    ('indhandling', _('indhandlingssted/produktionsanlæg'))
)


class Indberetning(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    indberetnings_type = models.TextField(choices=indberetnings_type_choices)
    virksomhed = models.ForeignKey(Virksomhed, on_delete=models.PROTECT, db_index=True)
    indberetters_cpr = models.TextField(validators=[validate_cpr])  # CPR fra medarbejder signatur eller nemid
    administrator = models.ForeignKey(get_user_model(), null=True,
                                      on_delete=models.PROTECT)  # only used when sudo is used
    afgiftsperiode = models.ForeignKey(Afgiftsperiode, on_delete=models.PROTECT, db_index=True)
    indberetningstidspunkt = models.DateTimeField(auto_now_add=True)
    navn = models.TextField()  # fartojs navn eller indhanlingssted/bygd

    def get_navn_display(self):
        if self.indberetnings_type == 'havgående':
            return _('Fartøjets navn')
        return _('indhandlingssted/Bygd')

    class Meta:
        ordering = ('indberetningstidspunkt',)


class IndberetningLinje(models.Model):
    # eksport: summer på kategori niveau
    # indhandling: summer på fiskearts niveau
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    indberetning = models.ForeignKey(Indberetning, on_delete=models.CASCADE, related_name='linjer')
    fiskeart = models.ForeignKey(FiskeArt, on_delete=models.PROTECT)
    kategori = models.ForeignKey(ProduktKategori, on_delete=models.PROTECT,
                                 null=True, blank=True)  # bruges ikke til inhandling
    salgsvægt = models.DecimalField(max_digits=20, decimal_places=2,
                                    verbose_name=_('Salgsvægt (kg)'))
    levende_vægt = models.DecimalField(max_digits=20, decimal_places=2,
                                       verbose_name=_('Levende vægt/helfisk mængde (kg)'))  # hel fisk
    salgspris = models.DecimalField(max_digits=20, decimal_places=2,
                                    verbose_name=_('Salgspris (kr.)'))


@receiver(post_save, sender=Indberetning, dispatch_uid='indberetning_store_navne')
def store_navne(sender, **kwargs):
    # store new names
    instance = kwargs['instance']
    if instance.indberetnings_type == 'indhandling':
        navne_type = 'indhandlings_sted'
    else:
        navne_type = 'fartøj'
    try:
        Navne.objects.create(virksomhed=instance.virksomhed, navn=instance.navn, type=navne_type)
    except IntegrityError:
        # navn all ready exists
        pass


def bilag_filepath(instance, filename):
    return 'bilag/{uuid}/{filename}'.format(uuid=instance.indberetning.uuid,
                                            filename=filename)


class Bilag(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    indberetning = models.ForeignKey(Indberetning, on_delete=models.PROTECT, related_name='bilag')
    bilag = models.FileField(upload_to=bilag_filepath)

    @property
    def filename(self):
        return os.path.basename(self.bilag.name)
