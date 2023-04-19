from django.core.management.base import BaseCommand
from indberetning.models import IndberetningLinje
from indberetning.models import set_ratenummer


class Command(BaseCommand):
    help = "Generates ratenummer for IndberetningLinjer that don't have any"

    def handle(self, *args, **options):
        for linje in IndberetningLinje.objects.filter(ratenummer_counter__isnull=True):
            set_ratenummer(None, instance=linje)
            linje.save(update_fields=("ratenummer_counter",))
