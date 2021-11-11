from django.db import models


class NamedModel(models.Model):
    class Meta:
        abstract = True
    navn = models.CharField(max_length=2048)
    beskrivelse = models.TextField(blank=True, default="")

    def __str__(self):
        return f"{self.navn}"


class FiskeArt(models):
    # en fiske art kan være, reje, Hellefisk, osv
    navn = models.TextField()  # Rejer


class Produkt(models):
    #  et produkt kan være:   Råfrosne skalrejer
    fisk = models.ForeignKey(FiskeArt, on_delete=models.PROTECT)
    navn = models.TextField()  # Råfrosne skalrejer


class Kategori(NamedModel):
    pass


class TypePost(models.Model):
    class Meta:
        abstract = True
    type = models.BooleanField(choices=[(False, "Procent"), (True, "Pr. kilo")])
    vaerdi = models.FloatField()


class BeregningsModelPrototype(NamedModel):
    pass


class BeregningsModelEksempel(NamedModel):
    prototype = models.ForeignKey(BeregningsModelPrototype, on_delete=models.CASCADE)
    justering_A = models.IntegerField(default=5)
    justering_B = models.DecimalField(max_digits=100, decimal_places=2, default=0.10)


class Afgiftstabel(NamedModel):
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)


class AfgiftsTabelPost(TypePost):
    afgiftstabel = models.ForeignKey(Afgiftstabel, related_name='poster', on_delete=models.CASCADE)
    nedre = models.FloatField()
    oevre = models.FloatField()


class BeregningsModelKategori(models.Model):
    beregningsmodel_eksempel = models.ForeignKey(BeregningsModelEksempel, on_delete=models.CASCADE)
    afgiftstabel = models.ForeignKey(Afgiftstabel, on_delete=models.CASCADE)
    fisk = models.ManyToManyField(FiskeArt)
    # Der er et eller andet mærkeligt for det må være produktet der styre afgiftsatsen og ikke fiske arten?


class Afgiftsperiode(NamedModel):
    dato_fra = models.DateField()
    dato_til = models.DateField()
    beregningsmodel = models.ForeignKey(BeregningsModelEksempel, on_delete=models.PROTECT)
    # TODO det skal nok være muligt at fjerne afgiftsperioden/indberetningsperioden fra selvbetjeningsløsningen


class SatsTabelPost(TypePost):
    afgiftsperiode = models.ForeignKey(Afgiftsperiode, on_delete=models.CASCADE)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    fiskeart = models.ForeignKey(FiskeArt, on_delete=models.CASCADE)



################################################################################



class Indberetter(models.Model):
    cpr_cvr_nummer = models.CharField(max_length=20)
    navn = models.CharField(max_length=2048, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    kontonummer = models.IntegerField(null=True)
    er_rederi = models.BooleanField(default=False)
    rederi_navn = models.CharField(max_length=2048, blank=True, null=True)
    rederi_adresse = models.CharField(max_length=2048, blank=True, null=True)
    rederi_postnummer_by = models.CharField(max_length=2048, blank=True, null=True)
    administrationsadresse_navn = models.CharField(max_length=2048, blank=True, null=True)
    administrationsadresse_adresse = models.CharField(max_length=2048, blank=True, null=True)
    administrationsadresse_postnummer_by = models.CharField(max_length=2048, blank=True, null=True)


class Indberetning(models.Model):
    #TODO der mangler en model til at gemme fartøjets/indhandlingsstedets navn, så det kan genbruges.
    indberetter = models.ForeignKey(Indberetter, on_delete=models.PROTECT)
    afgiftsperiode = models.ForeignKey(Afgiftsperiode, null=True, on_delete=models.PROTECT)
    indberetningstidspunkt = models.DateTimeField(auto_now_add=True)
    afgiftsberegningstidspunkt = models.DateTimeField(null=True, default=None)
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE) #Antager at med kategori der menes IndberetningsType (Fartøj/Fabrik(indhandlingsted))
    cpr_cvr = models.CharField(max_length=20, blank=True, default="")
    fartoejets_navn = models.CharField(max_length=2048, blank=True, null=True, verbose_name='fartøjets navn')
    fartoejets_hjemsted = models.CharField(max_length=2048, blank=True, null=True, verbose_name='fartøjets hjemsted')
    indhandlings_eller_produktionsanlaeg = models.CharField(max_length=20, blank=True, default="", verbose_name='indhandlings- eller produktionsanlæg')
    # TODO fartoejets_navn og indhandlings_eller_produktionsanlaeg kan slås sammen og det vil så være indberetningstypen der
    # styre meningen, ved at overskrive: get_navn_display()
    # det samme kan man gøre med salgspris(salgspris/indhandlingspris)
    indhandlers_cpr_cvr = models.CharField(max_length=20, blank=True, default="", verbose_name='indhandlers CPR/CVR')
    fiskeart = models.ForeignKey(FiskeArt, on_delete=models.PROTECT)
    levende_vaegt = models.IntegerField(blank=True, null=True, verbose_name='levende vægt')
    indhandlet_vaegt = models.IntegerField(blank=True, null=True, verbose_name='indhandlet vægt')
    vederlag_dkk = models.DecimalField(max_digits=100, decimal_places=2, default=0.00, verbose_name='vederlag DKK')
    salgspris_dkk = models.DecimalField(max_digits=100, decimal_places=2, default=0.00, verbose_name='salgspris DKK')
    salgsmaengde_vaegt = models.IntegerField(blank=True, null=True, verbose_name='salgsmængde vægt')
    yderligere_dokumentation = models.TextField(blank=True, default="")


class SummeretBeregnetIndberetning(models.Model):
    justering = models.BooleanField(default=False)
    afgift_til_betaling = models.DecimalField(max_digits=100, decimal_places=2)
    afstemt = models.BooleanField(default=False)
    bogfoert = models.BooleanField(default=False)
    sendt_til_prisme = models.BooleanField(default=False)


class BeregnetIndberetning(models.Model):
    indberetning = models.ForeignKey(Indberetning, on_delete=models.CASCADE)
    summeret_beregnet_indberetning = models.ForeignKey(SummeretBeregnetIndberetning, on_delete=models.PROTECT)
    beregningsmodel = models.ForeignKey(BeregningsModelEksempel, null=True, on_delete=models.PROTECT)
    afgiftstabel = models.ForeignKey(Afgiftstabel, null=True, on_delete=models.PROTECT)
    kladde = models.BooleanField(default=True)
    simuleret = models.BooleanField(default=True)
    transportpris_indgaar_i_salgspris = models.BooleanField(default=False)
    omregningsfaktor = models.DecimalField(max_digits=100, decimal_places=2)
    afgiftsgrundlag = models.DecimalField(max_digits=100, decimal_places=2)


class FormularFelt(models.Model):
    TYPE_INT = 1
    TYPE_STRING = 2
    TYPE_ENUM = 3
    type_choices = [
        (TYPE_INT, "Tal"),
        (TYPE_STRING, "Tekst"),
        (TYPE_ENUM, "Valg")
    ]
    navn = models.CharField(max_length=2048, blank=True, default="")
    type = models.PositiveSmallIntegerField(choices=type_choices)
    valideringsregel = models.CharField(max_length=2048, blank=True, default="")

    def __str__(self):
        return f"{self.navn} ({self.get_type_display()})"


class BeregningsModelFormularFelter(models.Model):
    FORMULAR_1 = "Formular1"
    FORMULAR_2 = "Formular2"
    FORMULAR_3 = "Formular3"
    FORMULAR_4 = "Formular4"
    formular_choices = (
        (FORMULAR_1, "Formular 1"),
        (FORMULAR_2, "Formular 2"),
        (FORMULAR_3, "Formular 3"),
        (FORMULAR_4, "Formular 4"),
    )
    formular = models.CharField(max_length=20, choices=formular_choices)
    beregningsmodelkategori = models.ForeignKey(BeregningsModelKategori, on_delete=models.CASCADE)
    formularfelt = models.ForeignKey(FormularFelt, on_delete=models.CASCADE)
