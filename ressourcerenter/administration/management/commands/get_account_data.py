from collections import defaultdict
from datetime import date

from administration.models import Faktura
from administration.prisme import Prisme
from django.core.management.base import BaseCommand
from django.utils import timezone

from ressourcerenter.administration.prisme import PrismeException


class Command(BaseCommand):
    help = "Get Prisme Kontoudtog"

    def handle(self, *args, **options):
        manglende_fakturaer = (
            Faktura.objects.filter(bogført=None)
            .order_by("oprettet")
            .select_related("virksomhed")
        )
        by_cvr = defaultdict(dict)
        for faktura in manglende_fakturaer:
            by_cvr[faktura.virksomhed.cvr][faktura.id] = faktura
        prisme = Prisme()
        for cvr, fakturaer in by_cvr.items():
            # Alle fakturaer hentes fra DB sorteret efter dato (ældste først) og indsættes i den rækkefølge i vores dict,
            # så første faktura her vil altid være den ældste.
            first_date = next(iter(fakturaer.values())).oprettet.date()
            # Hent kontoudtog fra første fakturadato til nu
            try:
                responses = prisme.get_account_data(cvr, first_date, timezone.now())
            except PrismeException:
                continue
            # For hver transaktion der optræder i kontoudtoget,
            # se om vi kan finde en matchende faktura og sæt den til at være bogført
            for response in responses:
                earliest_map = {}
                for transaction in response:
                    faktura_id = transaction.extern_invoice_number
                    if faktura_id is not None:
                        bogført_dato = (
                            date.fromisoformat(transaction.accounting_date)
                            if transaction.accounting_date
                            else date.today()
                        )
                        prior = earliest_map.get(faktura_id, None)
                        if prior is None or prior > bogført_dato:
                            earliest_map[faktura_id] = bogført_dato
                for faktura_id, bogført_dato in earliest_map.items():
                    faktura = by_cvr[cvr].get(int(faktura_id))
                    if faktura is not None:
                        faktura.bogført = bogført_dato
                        faktura.save(update_fields=["bogført"])
