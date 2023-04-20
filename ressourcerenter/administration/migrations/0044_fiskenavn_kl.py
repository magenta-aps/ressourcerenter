from django.db import migrations


def apply_migration(apps, schema_editor):
    FiskeArt = apps.get_model("administration", "FiskeArt")
    ProduktType = apps.get_model("administration", "ProduktType")
    FiskeArt.objects.filter(navn_dk="Hellefisk - Indhandling fra havgående").update(navn_gl="Qalerallit - avataasiorluni aalisarnermit tunisassiorfinnut tunisat")
    FiskeArt.objects.filter(navn_dk="Hellefisk - Indhandling fra kystnært").update(navn_gl="Qalerallit - sinerissamut qanittumi aalisarnermit tunisassiorfinnut tunisat")
    ProduktType.objects.filter(navn_dk="Hellefisk - Indhandling fra havgående").update(navn_gl="Qalerallit - avataasiorluni aalisarnermit tunisassiorfinnut tunisat")
    ProduktType.objects.filter(navn_dk="Hellefisk - Indhandling fra havgående - Hel fisk").update(navn_gl="Qalerallit - avataasiorluni aalisarnermit tunisassiorfinnut tunisat - Iluitsuutillugit")
    ProduktType.objects.filter(navn_dk="Hellefisk - Indhandling fra havgående - Filet").update(navn_gl="Qalerallit - avataasiorluni aalisarnermit tunisassiorfinnut tunisat - Nerpiit saaneeraajakkat")
    ProduktType.objects.filter(navn_dk="Hellefisk - Indhandling fra havgående - Saniatigut tunisassiat").update(navn_gl="Qalerallit - avataasiorluni aalisarnermit tunisassiorfinnut tunisat - Saniatigut tunisassiat")
    ProduktType.objects.filter(navn_dk="Hellefisk - Indhandling fra kystnært").update(navn_gl="Qalerallit - sinerissamut qanittumi aalisarnermit tunisassiorfinnut tunisat")
    ProduktType.objects.filter(navn_dk="Hellefisk - Indhandling fra kystnært - Hel fisk").update(navn_gl="Qalerallit - sinerissamut qanittumi aalisarnermit tunisassiorfinnut tunisat - Iluitsuutillugit")
    ProduktType.objects.filter(navn_dk="Hellefisk - Indhandling fra kystnært - Filet").update(navn_gl="Qalerallit - sinerissamut qanittumi aalisarnermit tunisassiorfinnut tunisat - Nerpiit saaneeraajakkat")
    ProduktType.objects.filter(navn_dk="Hellefisk - Indhandling fra kystnært - Saniatigut tunisassiat").update(navn_gl="Qalerallit - sinerissamut qanittumi aalisarnermit tunisassiorfinnut tunisat - Saniatigut tunisassiat")
    ProduktType.objects.filter(navn_dk="Reje - havgående licens").update(navn_gl="Raajat - avataasiorluni akuersissutaatilik")
    ProduktType.objects.filter(navn_dk="Reje - kystnær licens").update(navn_gl="Raajat - sinerissap qanittuani akuersissutaatilik")
    ProduktType.objects.filter(navn_dk="Reje - Svalbard og Barentshavet").update(navn_gl="Raajat - Svalbardip Barentsillu imartaa")


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0043_hellefisk'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
