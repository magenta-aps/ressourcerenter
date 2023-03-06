from django.db import migrations


def apply_migration(apps, schema_editor):

    SkemaType = apps.get_model('administration', 'SkemaType')
    SkemaType.objects.filter(id=1).update(
        navn_gl="Angallatit avataasiutit aammalu sinerissap qanittuani raajarniutit - angallatit tunisassiortut"
    )
    SkemaType.objects.filter(id=2).update(
        navn_gl="Tulaassinerit - Tunisassiorfinnit nalunaarutit / Avataasiorluni aalisarneq aammalu sinerissap qanittuani raajarniarneq"
    )
    SkemaType.objects.filter(id=3).update(
        navn_gl="Sinerissap qanittuani raajaanngitsunik aalisakkanik allanik aalisarneq - Tunisassiorfinnit nalunaarutit"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0028_auto_20230303_0950'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
