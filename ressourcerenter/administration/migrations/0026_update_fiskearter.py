from django.db import migrations


def apply_migration(apps, schema_editor):
    update_fiskearter(apps)
    update_produkttyper(apps)


def update_fiskearter(apps):

    Fiskeart = apps.get_model('administration', 'Fiskeart')
    Fiskeart.objects.filter(navn_dk="Torsk").update(navn_gl="Saarullik")
    Fiskeart.objects.filter(navn_dk="Hellefisk").update(navn_gl="Qalerallit")
    Fiskeart.objects.filter(navn_dk="Kuller").update(navn_gl="Misaqqarnat")
    Fiskeart.objects.filter(navn_dk="Sej").update(navn_gl="Saarulliusaat")
    Fiskeart.objects.filter(navn_dk="Rødfisk").update(navn_gl="Suluppaakkat")
    Fiskeart.objects.filter(navn_dk="Sild").update(navn_gl="Ammassassuit")
    Fiskeart.objects.filter(navn_dk="Lodde").update(navn_gl="Ammassat")
    Fiskeart.objects.filter(navn_dk="Makrel").update(navn_gl="Avaleraasartuut")
    Fiskeart.objects.filter(navn_dk="Blåhvilling").update(navn_gl="Saarullernaq")
    Fiskeart.objects.filter(navn_dk="Guldlaks").update(navn_gl="Guldlaks")

    Fiskeart.objects.filter(navn_dk="Reje - havgående licens").update(navn_gl="Raajat - avataasiorluni akuersissutaatilik")
    Fiskeart.objects.filter(navn_dk="Reje - kystnær licens").update(navn_gl="Raajat - sinerissap qanittuani akuersissutaatilik")
    Fiskeart.objects.filter(navn_dk="Reje - Svalbard og Barentshavet").update(navn_gl="Raajat - Svaldbardip Barentsillu imartaa")


def update_produkttyper(apps):

    ProduktType = apps.get_model('administration', 'ProduktType')
    ProduktType.objects.filter(navn_dk="Torsk", ).update(navn_gl="Saarullik")
    ProduktType.objects.filter(navn_dk="Torsk - Hel fisk", ).update(navn_gl="Saarullik")
    ProduktType.objects.filter(navn_dk="Torsk - Filet", ).update(navn_gl="Saarullik")
    ProduktType.objects.filter(navn_dk="Torsk - Biprodukter", ).update(navn_gl="Saarullik")
    ProduktType.objects.filter(navn_dk="Hellefisk").update(navn_gl="Qalerallit")
    ProduktType.objects.filter(navn_dk="Hellefisk - Hel fisk").update(navn_gl="Qalerallit - Iluitsuutillugit")
    ProduktType.objects.filter(navn_dk="Hellefisk - Filet").update(navn_gl="Qalerallit - Nerpiit saaneeraajakkat")
    ProduktType.objects.filter(navn_dk="Hellefisk - Biprodukter").update(navn_gl="Qalerallit - Saniatigut tunisassiat")
    ProduktType.objects.filter(navn_dk="Kuller").update(navn_gl="Saarullernat")
    ProduktType.objects.filter(navn_dk="Kuller - Hel fisk").update(navn_gl="Misaqqarnat - Iluitsuutillugit")
    ProduktType.objects.filter(navn_dk="Kuller - Filet").update(navn_gl="Misaqqarnat - Nerpik saaniiakkat")
    ProduktType.objects.filter(navn_dk="Kuller - Biprodukter").update(navn_gl="Misaqqarnat - Saniatigut tunisassiat")
    ProduktType.objects.filter(navn_dk="Sej").update(navn_gl="Saarulliusaat")
    ProduktType.objects.filter(navn_dk="Sej - Hel fisk").update(navn_gl="Saarulliusaat - Iiluitsuutillugit")
    ProduktType.objects.filter(navn_dk="Sej - Filet").update(navn_gl="Saarulliusaat - Nerpik saaniiakkat")
    ProduktType.objects.filter(navn_dk="Sej - Biprodukter").update(navn_gl="Saarulliusaat - Saniatigut tunisassiat")
    ProduktType.objects.filter(navn_dk="Rødfisk").update(navn_gl="Suluppaakkat")
    ProduktType.objects.filter(navn_dk="Rødfisk - Hel fisk").update(navn_gl="Suluppaakkat - Iluitsuutillugit")
    ProduktType.objects.filter(navn_dk="Rødfisk - Filet").update(navn_gl="Suluppaakkat - Nerpik saaniiakkat")
    ProduktType.objects.filter(navn_dk="Rødfisk - Biprodukter").update(navn_gl="Suluppaakkat - Saniatigut tunisassiat")

    ProduktType.objects.filter(navn_dk="Reje - havgående licens - Biprodukter").update(navn_gl="Raajat - avataasiorluni akuersissutaatilik - Saniatigut tunisassiat")
    ProduktType.objects.filter(navn_dk="Reje - havgående licens - Industrirejer-sækkerejer").update(navn_gl="Raajat - avataasiorluni akuersissutaatilik - Raajat suliffissuarni tunisassiassat - Raajat puunut poortukkat")
    ProduktType.objects.filter(navn_dk="Reje - havgående licens - Råfrosne skalrejer").update(navn_gl="Raajat - avataasiorluni akuersissutaatilik - Raajat qalipallit uunneqanngitsut qerisut")
    ProduktType.objects.filter(navn_dk="Reje - havgående licens - Søkogte skalrejer").update(navn_gl="Raajat - avataasiorluni akuersissutaatilik - Raajat avataani uutat")

    ProduktType.objects.filter(navn_dk="Reje - kystnær licens - Biprodukter").update(navn_gl="Raajat - sinerissap qanittuani akuersissutaatilik - Saniatigut tunisassiat")
    ProduktType.objects.filter(navn_dk="Reje - kystnær licens - Industrirejer-sækkerejer").update(navn_gl="Raajat - sinerissap qanittuani akuersissutaatilik - Saniatigut tunisassiat - Raajat suliffissuarni tunisassiassat - raajat puunut poortukkat")
    ProduktType.objects.filter(navn_dk="Reje - kystnær licens - Råfrosne skalrejer").update(navn_gl="Raajat - sinerissap qanittuani akuersissutaatilik - Raajat qalipallit uunneqanngitsut qerisut")
    ProduktType.objects.filter(navn_dk="Reje - kystnær licens - Søkogte skalrejer").update(navn_gl="Raajat - sinerissap qanittuani akuersissutaatilik - Raajat avataani uutat")

    ProduktType.objects.filter(navn_dk="Reje - Svalbard og Barentshavet - Biprodukter").update(navn_gl="Raajat - Svalbardip Barentsillu imartaa - Saniatigut tunisassiat")
    ProduktType.objects.filter(navn_dk="Reje - Svalbard og Barentshavet - Industrirejer-sækkerejer").update(navn_gl="Raajat - Svalbardip Barentsillu imartaa - Raajat suliffissuarni tunisassiassat - Raajat puunut poortukkat")
    ProduktType.objects.filter(navn_dk="Reje - Svalbard og Barentshavet - Råfrosne skalrejer").update(navn_gl="Raajat - Svalbardip Barentsillu imartaa - Raajat qalipallit uunneqanngitsut qerisut")
    ProduktType.objects.filter(navn_dk="Reje - Svalbard og Barentshavet - Søkogte skalrejer").update(navn_gl="Raajat - Svalbardip Barentsillu imartaa - Raajat avataani uutat")

    ProduktType.objects.filter(fiskeart__navn_dk="Sild", fartoej_groenlandsk=False).update(navn_gl="Ammassassuit, kalaallit angallatiginngisaat")
    ProduktType.objects.filter(fiskeart__navn_dk="Sild", fartoej_groenlandsk=True).update(navn_gl="Ammassassuit, kalaallit angallataat")
    ProduktType.objects.filter(fiskeart__navn_dk="Lodde", fartoej_groenlandsk=False).update(navn_gl="Ammassat, kalaallit aalisariutiginngisaat")
    ProduktType.objects.filter(fiskeart__navn_dk="Lodde", fartoej_groenlandsk=True).update(navn_gl="Ammassat, kalaallit aalisariutaat")
    ProduktType.objects.filter(fiskeart__navn_dk="Makrel", fartoej_groenlandsk=False).update(navn_gl="Avaleraasartuut, kalaallit aalisariutiginngisaat")
    ProduktType.objects.filter(fiskeart__navn_dk="Makrel", fartoej_groenlandsk=True).update(navn_gl="Avaleraasartuut, kalaallit aalisariutaat")
    ProduktType.objects.filter(fiskeart__navn_dk="Blåhvilling", fartoej_groenlandsk=False).update(navn_gl="Saarullernaq, kalaallit angallataat")
    ProduktType.objects.filter(fiskeart__navn_dk="Blåhvilling", fartoej_groenlandsk=True).update(navn_gl="Saarullernaq, kalaallit angallatiginngisaat")
    ProduktType.objects.filter(fiskeart__navn_dk="Guldlaks", fartoej_groenlandsk=False).update(navn_gl="Guldlaks, kalaallit angallatiginngisaat")
    ProduktType.objects.filter(fiskeart__navn_dk="Guldlaks", fartoej_groenlandsk=True).update(navn_gl="Guldlaks, kalaallit angallataat")


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0025_update_perioder'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
