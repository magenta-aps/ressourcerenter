from django.db import migrations


def apply_migration(apps, schema_editor):

    Indhandlingssted = apps.get_model('indberetning', 'Indhandlingssted')
    for stedkode, navn in (
        (10766, 'Nuussuaq ved Upernavik'),
        (10469, 'Nuussuaq i Nuuk'),
        (10756, 'Illorsuit ved Uummannaq'),
    ):
        Indhandlingssted.objects.update_or_create(
            stedkode=stedkode,
            defaults={
                'navn': navn,
            }
        )
    Indhandlingssted.objects.filter(stedkode=10326).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0019_indhandlingssteder_bruttoliste'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
