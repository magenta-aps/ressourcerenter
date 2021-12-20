import os
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from administration.models import SkemaType, Afgiftsperiode, ProduktType
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
    skematype = models.ForeignKey(SkemaType, on_delete=models.CASCADE)
    indberetnings_type = models.TextField(choices=indberetnings_type_choices)
    virksomhed = models.ForeignKey(Virksomhed, on_delete=models.PROTECT, db_index=True)
    indberetters_cpr = models.TextField(validators=[validate_cpr])  # CPR fra medarbejder signatur eller nemid
    administrator = models.ForeignKey(get_user_model(), null=True,
                                      on_delete=models.PROTECT)  # only used when sudo is used
    afgiftsperiode = models.ForeignKey(Afgiftsperiode, on_delete=models.PROTECT, db_index=True)
    indberetningstidspunkt = models.DateTimeField(auto_now_add=True)
    afstemt = models.BooleanField(default=False)

    def get_navn_display(self):
        if self.indberetnings_type == 'havgående':
            return _('Fartøjets navn')
        return _('indhandlingssted/Bygd')

    def get_fishcategories_string(self):
        return '; '.join([linje.produkttype.fiskeart.navn_dk for linje in self.linjer.all()])

    class Meta:
        ordering = ('indberetningstidspunkt',)


class IndberetningLinje(models.Model):
    # eksport: summer på kategori niveau
    # indhandling: summer på fiskearts niveau
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField()  # fartojs navn eller indhandlingssted/bygd
    indberetning = models.ForeignKey(Indberetning, on_delete=models.CASCADE, related_name='linjer')
    produkttype = models.ForeignKey(ProduktType, on_delete=models.PROTECT)

    salgsvægt = models.DecimalField(max_digits=20, decimal_places=2,
                                    verbose_name=_('Salgsvægt (kg)'))
    levende_vægt = models.DecimalField(max_digits=20, decimal_places=2,
                                       verbose_name=_('Levende vægt/helfisk mængde (kg)'))  # hel fisk
    salgspris = models.DecimalField(max_digits=20, decimal_places=2, null=True,
                                    verbose_name=_('Salgspris (kr.)'))
    transporttillæg = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                          verbose_name=_('Transporttillæg (kr)'))
    bonus = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True,
                                verbose_name=_('Bonus og andet vederlag (kr)'))

    note = models.TextField()


@receiver(post_save, sender=IndberetningLinje, dispatch_uid='indberetning_store_navne')
def store_navne(sender, **kwargs):
    # store new names
    instance = kwargs['instance']
    if instance.indberetning.indberetnings_type == 'indhandling':
        navne_type = 'indhandlings_sted'
    else:
        navne_type = 'fartøj'
    try:
        Navne.objects.create(virksomhed=instance.indberetning.virksomhed, navn=instance.navn, type=navne_type)
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
