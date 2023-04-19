import datetime
import random
from administration.models import Afgiftsperiode, BeregningsModel2021, SkemaType
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from indberetning.models import (
    Indberetning,
    Virksomhed,
    IndberetningLinje,
    Indhandlingssted,
)


class Command(BaseCommand):
    help = "Create sample data only for development environments"

    def handle(self, *args, **options):
        random.seed(10)

        virksomheder = []
        virksomhed_counters = list(range(9))
        random.shuffle(virksomhed_counters)  # Shuffle to check that sorting works
        for virksomhed_counter in virksomhed_counters:
            virksomhed, _ = Virksomhed.objects.get_or_create(
                cvr=str(12345670 + virksomhed_counter),
                defaults={
                    "navn": "Testvirksomhed_%d" % virksomhed_counter,
                    "sted": Indhandlingssted.objects.order_by("?")[0],
                },
            )
            virksomheder.append(virksomhed)

        beregningsmodel, _ = BeregningsModel2021.objects.get_or_create(
            navn="TestBeregningsModel",
        )

        indhandlingssteder = Indhandlingssted.objects.all()

        alle_fartoejer = ["Systemoprettet fartøj_%d" % i for i in range(6)]
        random.shuffle(alle_fartoejer)  # Shuffle to check that sorting works

        for periode in Afgiftsperiode.objects.all():
            fartoejer = random.sample(alle_fartoejer, 3)
            periode.beregningsmodel = beregningsmodel
            periode.save()

            virksomhed = random.choice(virksomheder)
            indberetninger_exist = virksomhed.indberetning_set.exists()

            if not indberetninger_exist:
                # Create all entries at 10 am on the given day
                create_datetime = timezone.datetime.combine(
                    periode.dato_fra, datetime.time(10, 0)
                )
                create_datetime = timezone.make_aware(create_datetime)

                for skematype in SkemaType.objects.all().order_by("id"):
                    if skematype.id == 1:
                        indberetning = Indberetning.objects.create(
                            skematype=skematype,
                            virksomhed=virksomhed,
                            afgiftsperiode=periode,
                            indberetters_cpr="123456-1955",
                            afstemt=random.choice([True, False]),
                        )

                        indberetning.indberetningstidspunkt = create_datetime
                        indberetning.save()
                        create_datetime = create_datetime + datetime.timedelta(days=1)

                        alle_fiskearter = list(skematype.fiskeart_set.all())
                        fiskearter = random.sample(alle_fiskearter, 3)

                        for fiskeart in fiskearter:
                            for produkttype in fiskeart.produkttype_set.all():
                                for i in range(1, random.randint(1, 2)):
                                    x = random.randint(20, 50)
                                    IndberetningLinje.objects.create(
                                        indberetning=indberetning,
                                        fartøj_navn=random.choice(fartoejer),
                                        produktvægt=x,
                                        levende_vægt=2 * x,
                                        salgspris=40 * x,
                                        transporttillæg=Decimal(100.0),
                                        kommentar="Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden",
                                        produkttype=produkttype,
                                    )

                    if skematype.id == 2:
                        # Two types of product types, identified by pelagisk true/false
                        # Two types of trading, identified by whether trading is done from a boat or on land
                        for pelagisk in [True, False]:
                            indberetning = Indberetning.objects.create(
                                skematype=skematype,
                                virksomhed=virksomhed,
                                afgiftsperiode=periode,
                                indberetters_cpr="123456-1955",
                                afstemt=random.choice([True, False]),
                            )
                            # Set date in the past
                            indberetning.indberetningstidspunkt = create_datetime
                            indberetning.save()
                            create_datetime = create_datetime + datetime.timedelta(
                                days=1
                            )

                            alle_fiskearter = list(
                                skematype.fiskeart_set.filter(pelagisk=pelagisk)
                            )
                            fiskearter = random.sample(alle_fiskearter, 3)

                            for fiskeart in fiskearter:
                                for produkttype in fiskeart.produkttype_set.filter(
                                    gruppe=None
                                ):
                                    for i in range(1, random.randint(1, 2)):
                                        x = random.randint(20, 50)
                                        IndberetningLinje.objects.create(
                                            indberetning=indberetning,
                                            fartøj_navn=random.choice(fartoejer),
                                            indhandlingssted=random.choice(
                                                indhandlingssteder
                                            ),
                                            produktvægt=x,
                                            levende_vægt=2 * x,
                                            salgspris=40 * x,
                                            kommentar="Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden",
                                            produkttype=produkttype,
                                        )

                    if skematype.id == 3:
                        sted = random.choice(indhandlingssteder)
                        indberetning = Indberetning.objects.create(
                            skematype=skematype,
                            virksomhed=virksomhed,
                            afgiftsperiode=periode,
                            indberetters_cpr="123456-1955",
                            afstemt=random.choice([True, False]),
                        )

                        indberetning.indberetningstidspunkt = create_datetime
                        indberetning.save()
                        create_datetime = create_datetime + datetime.timedelta(days=1)

                        for fiskeart in skematype.fiskeart_set.all():
                            for produkttype in fiskeart.produkttype_set.all():
                                for i in range(1, random.randint(1, 2)):
                                    x = random.randint(20, 50)
                                    IndberetningLinje.objects.create(
                                        indberetning=indberetning,
                                        indhandlingssted=sted,
                                        produktvægt=None,  # Skematype 3 bruger ikke produktvægt jf. #48022
                                        levende_vægt=2 * x,
                                        salgspris=40 * x,
                                        kommentar="Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden",
                                        produkttype=produkttype,
                                    )
