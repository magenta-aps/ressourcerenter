from django.db import migrations


def apply_migration(apps, schema_editor):
    BeregningsModel2021 = apps.get_model('administration', 'BeregningsModel2021')
    BeregningsModel2021.objects.create(
        navn="BeregningsModel2021",
    )


def revert_migration(apps, schema_editor):
    BeregningsModel2021 = apps.get_model('administration', 'BeregningsModel2021')
    BeregningsModel2021.objects.filter(navn="BeregningsModel2021").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0021_indhandlingssteder'),
    ]

    operations = [
        migrations.RunPython(apply_migration, reverse_code=revert_migration)
    ]
