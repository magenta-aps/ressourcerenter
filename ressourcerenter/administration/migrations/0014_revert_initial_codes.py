from django.db import migrations


# This reverts the changes made in 0012_initial_codes, that have been rolled out to test
# We may decide to collapse these migrations before rollout to prod, thus deleting both files
def apply_migration(apps, schema_editor):
    G69Code = apps.get_model('administration', 'G69Code')
    G69Code.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0013_set_fiskeart_koder'),
    ]

    operations = [
        migrations.RunPython(apply_migration)
    ]
