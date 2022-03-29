from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils import timezone

from administration.models import Afgiftsperiode, BeregningsModel2021, SkemaType
from indberetning.models import Indberetning, Virksomhed, IndberetningLinje, Indhandlingssted
from decimal import Decimal

import datetime
import random


class Command(BaseCommand):
    help = 'Create sample data only for development environments'

    def handle(self, *args, **options):
        if settings.DEBUG is False:
            print('DEBUG needs to be True (dev-environment)')
            return

        virksomhed, _ = Virksomhed.objects.update_or_create(cvr='12345678', defaults={'navn': 'Testvirksomhed'})

        try:
            beregningsmodel = BeregningsModel2021.objects.create(
                navn='TestBeregningsModel',
                transport_afgift_rate=Decimal(1),
            )
        except IntegrityError:
            beregningsmodel = BeregningsModel2021.objects.get(navn='TestBeregningsModel')
            beregningsmodel.transport_afgift_rate = Decimal(1)
            beregningsmodel.save()

        indhandlingssteder = []
        for navn, stedkode in (('Nuuk', '1111'), ('Sisimiut', '2222'), ('Ilulissat', '3333')):
            try:
                sted = Indhandlingssted.objects.get(navn=navn)
            except Indhandlingssted.DoesNotExist:
                sted = Indhandlingssted.objects.create(navn=navn, stedkode=stedkode)
            indhandlingssteder.append(sted)

        indberetninger_exist = Indberetning.objects.exists()

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
                                                                     kommentar='Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden',
                                                                     produkttype=produkttype)

                    if skematype.id == 2:
                        # Two types of product types, identified by pelagisk true/false
                        # Two types of trading, identified by whether trading is done from a boat or on land
                        for indhandlingssted, fartoej_navn, pelagisk in (
                            (indhandlingssteder[0], None, True),
                            (indhandlingssteder[1], None, False),
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
                        sted = indhandlingssteder[2]
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
