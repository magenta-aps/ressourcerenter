from django.core.management.base import BaseCommand
from django.utils import timezone
from administration.prisme import Prisme
from administration.models import Faktura
from datetime import date


class Command(BaseCommand):
    help = "Get Prisme Kontoudtog"

    def handle(self, *args, **options):
        manglende_fakturaer = (
            Faktura.objects.filter(bogført=None)
            .order_by("oprettet")
            .select_related("virksomhed")
        )
        by_cvr = {}
        for faktura in manglende_fakturaer:
            cvr = faktura.virksomhed.cvr
            if cvr not in by_cvr:
                by_cvr[cvr] = {}
            by_cvr[cvr][faktura.id] = faktura

        prisme = Prisme()
        for cvr, fakturaer in by_cvr.items():
            # Alle fakturaer hentes fra DB sorteret efter dato (ældste først) og indsættes i den rækkefølge i vores dict,
            # så første faktura her vil altid være den ældste.
            first_date = next(iter(fakturaer.values())).oprettet.date()

            # Hent kontoudtog fra første fakturadato til nu
            responses = prisme.get_account_data(cvr, first_date, timezone.now())

            # For hver transaktion der optræder i kontoudtoget,
            # se om vi kan finde en matchende faktura og sæt den til at være bogført
            for response in responses:
                for transaction in response:
                    faktura_id = transaction.extern_invoice_number
                    if faktura_id is not None:
                        bogført_dato = (
                            date.fromisoformat(transaction.accounting_date)
                            if transaction.accounting_date
                            else date.today()
                        )
                        faktura = by_cvr[cvr].get(int(faktura_id))
                        if faktura is not None:
                            faktura.bogført = bogført_dato
                            faktura.save(update_fields=["bogført"])
