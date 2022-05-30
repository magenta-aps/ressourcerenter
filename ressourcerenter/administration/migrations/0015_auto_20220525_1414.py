# Generated by Django 3.2.9 on 2022-05-25 12:05

from django.db import migrations


def apply_migration(apps, schema_editor):
    ProduktType = apps.get_model('administration', 'ProduktType')
    ProduktType.objects.filter(navn_dk__contains='Hel fisk').update(ordering=1)
    ProduktType.objects.filter(navn_dk__contains='Filet').update(ordering=2)
    ProduktType.objects.filter(navn_dk__contains='Råfrosne skalrejer').update(ordering=1)
    ProduktType.objects.filter(navn_dk__contains='Søkogte skalrejer').update(ordering=2)
    ProduktType.objects.filter(navn_dk__contains='Industrirejer-sækkerejer').update(ordering=3)
    ProduktType.objects.filter(navn_dk__contains='Biprodukter').update(ordering=4)


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0015_auto_20220525_1405'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
