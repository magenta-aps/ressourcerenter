from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils import timezone

from administration.models import Afgiftsperiode, BeregningsModel2021, SkemaType
from indberetning.models import Indberetning, Virksomhed, IndberetningLinje
from decimal import Decimal

import datetime


class Command(BaseCommand):
    help = 'Create sample data only for development environments'

    def handle(self, *args, **options):
        if settings.DEBUG is False:
            print('DEBUG needs to be True (dev-environment)')
            return

        virksomhed, _ = Virksomhed.objects.get_or_create(cvr='12345678')

        try:
            beregningsmodel = BeregningsModel2021.objects.create(
                navn='TestBeregningsModel',
                transport_afgift_rate=Decimal(1),
            )
        except IntegrityError:
            beregningsmodel = BeregningsModel2021.objects.get(navn='TestBeregningsModel')
            beregningsmodel.transport_afgift_rate = Decimal(1)
            beregningsmodel.save()

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
                                IndberetningLinje.objects.create(indberetning=indberetning,
                                                                 fartøj_navn=fartoej,
                                                                 salgsvægt=10,
                                                                 levende_vægt=20,
                                                                 salgspris=400,
                                                                 kommentar='Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden',
                                                                 produkttype=produkttype)

                    if skematype.id == 2:
                        # Two types of product types, identified by pelagisk true/false
                        # Two types of trading, identified by whether trading is done from a boat or on land
                        for indhandlingssted, fartoej_navn, pelagisk in (
                            ('Bygd for indhandling', None, True),
                            ('Bygd for indhandling', None, False),
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
                                    IndberetningLinje.objects.create(indberetning=indberetning,
                                                                     fartøj_navn=fartoej_navn,
                                                                     indhandlingssted=indhandlingssted,
                                                                     salgsvægt=10,
                                                                     levende_vægt=20,
                                                                     salgspris=400,
                                                                     kommentar='Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden',
                                                                     produkttype=produkttype)

                    if skematype.id == 3:
                        sted = 'Bygd for indhandling'
                        indberetning = Indberetning.objects.create(skematype=skematype,
                                                                   virksomhed=virksomhed,
                                                                   afgiftsperiode=periode,
                                                                   indberetters_cpr='123456-1955')

                        indberetning.indberetningstidspunkt = create_datetime
                        indberetning.save()
                        create_datetime = create_datetime + datetime.timedelta(days=1)

                        for fiskeart in skematype.fiskeart_set.all():
                            for produkttype in fiskeart.produkttype_set.all():
                                IndberetningLinje.objects.create(indberetning=indberetning,
                                                                 indhandlingssted=sted,
                                                                 salgsvægt=10,
                                                                 levende_vægt=20,
                                                                 salgspris=400,
                                                                 kommentar='Her er en lang kommentar som er meget lang for at demonstrere hvordan vi håndtererer en lang kommentar som bliver bred på siden',
                                                                 produkttype=produkttype)
