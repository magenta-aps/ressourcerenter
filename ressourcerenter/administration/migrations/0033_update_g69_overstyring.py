from django.db import migrations


def apply_migration(apps, schema_editor):
    Fiskeart = apps.get_model('administration', 'Fiskeart')
    Fiskeart.objects.filter(navn_dk__startswith="Reje").update(g69_overstyringskode='241112242040197')
    Fiskeart.objects.filter(navn_dk__startswith="Hellefisk").update(g69_overstyringskode='241125242040197')


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0032_auto_20230316_0907'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
