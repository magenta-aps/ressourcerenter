import datetime
import random
from administration.models import Afgiftsperiode, BeregningsModel2021, SkemaType
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils import timezone
from indberetning.models import Indberetning, Virksomhed, IndberetningLinje, Indhandlingssted


class Command(BaseCommand):
    help = 'Create sample data only for development environments'

    def add_arguments(self, parser):
        parser.add_argument('cvr', type=str)

    def handle(self, *args, **options):

        virksomhed, _ = Virksomhed.objects.get_or_create(
            cvr=options['cvr'],
            defaults={
                'navn': 'Testvirksomhed',
                'sted': Indhandlingssted.objects.get(navn='Nuuk')
            }
        )

        try:
            beregningsmodel = BeregningsModel2021.objects.create(
                navn='TestBeregningsModel',
                transport_afgift_rate=Decimal(1),
            )
        except IntegrityError:
            beregningsmodel = BeregningsModel2021.objects.get(navn='TestBeregningsModel')
            beregningsmodel.transport_afgift_rate = Decimal(1)
            beregningsmodel.save()

        indhandlingssteder = Indhandlingssted.objects.all()
        indberetninger_exist = virksomhed.indberetning_set.exists()

        for periode in Afgiftsperiode.objects.all():
            periode.beregningsmodel = beregningsmodel
            periode.save()

            if not indberetninger_exist:
                # Create all entries at 10 am on the given day
                create_datetime = timezone.datetime.combine(periode.dato_fra, datetime.time(10, 0))
                create_datetime = timezone.make_aware(create_datetime)

                for skematype in SkemaType.objects.all().order_by('id'):

                    if skematype.id == 1:
                        fartoej = 'Systemoprettet fartøj'
                        indberetning = Indberetning.objects.create(skematype=skematype,
                                                                   virksomhed=virksomhed,
                                                                   afgiftsperiode=periode,
                                                                   indberetters_cpr='123456-1955')

                        indberetning.indberetningstidspunkt = create_datetime
                        indberetning.save()
                        create_datetime = create_datetime + datetime.timedelta(days=1)

                        for fiskeart in skematype.fiskeart_set.all():
                            for produkttype in fiskeart.produkttype_set.all():
                                for i in range(1, random.randint(1, 10)):
                                    x = random.randint(10, 50)
                                    IndberetningLinje.objects.create(indberetning=indberetning,
                                                                     fartøj_navn=fartoej,
                                                                     produktvægt=x,
                                                                     levende_vægt=2*x,
                                                                     salgspris=40*x,
                                                                     transporttillæg=Decimal(100.0),
                                                                     kommentar='Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden',
                                                                     produkttype=produkttype)

                    if skematype.id == 2:
                        # Two types of product types, identified by pelagisk true/false
                        # Two types of trading, identified by whether trading is done from a boat or on land
                        for indhandlingssted, fartoej_navn, pelagisk in (
                            (random.choice(indhandlingssteder), None, True),
                            (random.choice(indhandlingssteder), None, False),
                            (None, 'Systemoprettet fartøj', True),
                            (None, 'Systemoprettet fartøj', False),
                        ):
                            indberetning = Indberetning.objects.create(skematype=skematype,
                                                                       virksomhed=virksomhed,
                                                                       afgiftsperiode=periode,
                                                                       indberetters_cpr='123456-1955')
                            # Set date in the past
                            indberetning.indberetningstidspunkt = create_datetime
                            indberetning.save()
                            create_datetime = create_datetime + datetime.timedelta(days=1)

                            fiskeart_qs = skematype.fiskeart_set.filter(pelagisk=pelagisk)

                            for fiskeart in fiskeart_qs:
                                for produkttype in fiskeart.produkttype_set.all():
                                    for i in range(1, random.randint(1, 10)):
                                        x = random.randint(10, 50)
                                        IndberetningLinje.objects.create(indberetning=indberetning,
                                                                         fartøj_navn=fartoej_navn,
                                                                         indhandlingssted=indhandlingssted,
                                                                         produktvægt=x,
                                                                         levende_vægt=2*x,
                                                                         salgspris=40*x,
                                                                         kommentar='Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden',
                                                                         produkttype=produkttype)

                    if skematype.id == 3:
                        sted = random.choice(indhandlingssteder)
                        indberetning = Indberetning.objects.create(skematype=skematype,
                                                                   virksomhed=virksomhed,
                                                                   afgiftsperiode=periode,
                                                                   indberetters_cpr='123456-1955')

                        indberetning.indberetningstidspunkt = create_datetime
                        indberetning.save()
                        create_datetime = create_datetime + datetime.timedelta(days=1)

                        for fiskeart in skematype.fiskeart_set.all():
                            for produkttype in fiskeart.produkttype_set.all():
                                for i in range(1, random.randint(1, 10)):
                                    x = random.randint(10, 50)
                                    IndberetningLinje.objects.create(indberetning=indberetning,
                                                                     indhandlingssted=sted,
                                                                     produktvægt=x,
                                                                     levende_vægt=2*x,
                                                                     salgspris=40*x,
                                                                     kommentar='Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden',
                                                                     produkttype=produkttype)
