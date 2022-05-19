from django.db import migrations


def apply_migration(apps, schema_editor):

    FiskeArt = apps.get_model('administration', 'FiskeArt')
    FiskeArt.objects.filter(navn_dk='Makrel').update(kode=1)
    FiskeArt.objects.filter(navn_dk='Sild').update(kode=2)
    FiskeArt.objects.filter(navn_dk='Lodde').update(kode=3)
    FiskeArt.objects.filter(navn_dk='Blåhvilling').update(kode=4)
    FiskeArt.objects.filter(navn_dk='Guldlaks').update(kode=5)
    FiskeArt.objects.filter(navn_dk='Hellefisk').update(kode=6)
    FiskeArt.objects.filter(navn_dk='Torsk').update(kode=7)
    FiskeArt.objects.filter(navn_dk='Kuller').update(kode=8)
    FiskeArt.objects.filter(navn_dk='Sej').update(kode=9)
    FiskeArt.objects.filter(navn_dk='Rødfisk').update(kode=10)
    FiskeArt.objects.filter(navn_dk='Reje - havgående licens').update(kode=11)
    FiskeArt.objects.filter(navn_dk='Reje - kystnær licens').update(kode=12)
    FiskeArt.objects.filter(navn_dk='Reje - Svalbard og Barentshavet').update(kode=13)


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0012_additional_indhandlingssteder'),
        ('administration', '0012_initial_codes'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
