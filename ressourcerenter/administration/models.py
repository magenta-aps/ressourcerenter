from django.db import models
from uuid import uuid4


class Afgiftsperiode(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField()
    vis_i_indberetning = models.BooleanField(default=False)

    def __str__(self):
        return self.navn


class FiskeArt(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField(unique=True)
    beskrivelse = models.TextField()

    def __str__(self):
        return self.navn


class Kategori(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4)
    navn = models.TextField(unique=True)  # Hel fisk, filet, bi-produkt
    beskrivelse = models.TextField()
