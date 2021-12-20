from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from administration.models import Afgiftsperiode, FiskeArt, ProduktType, BeregningsModel2021, SkemaType
from indberetning.models import Indberetning, Virksomhed, IndberetningLinje
from datetime import date
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample data only for development environments'

    def handle(self, *args, **options):
        if settings.DEBUG is False:
            print('DEBUG needs to be True (dev-environment)')
            return

        afgiftsperiode1, _ = Afgiftsperiode.objects.get_or_create(navn='4. kvartal 2021', vis_i_indberetning=True, dato_fra=date(2021, 10, 1), dato_til=date(2021, 12, 31))
        afgiftsperiode2, _ = Afgiftsperiode.objects.get_or_create(navn='3. kvartal 2021', vis_i_indberetning=True, dato_fra=date(2021, 7, 1), dato_til=date(2021, 9, 30))
        skematype, _ = SkemaType.objects.get_or_create(id=1, defaults={'navn_dk': 'Havgående fartøjer og kystnære rejefartøjer - producerende fartøjer'})
        fiskeart, _ = FiskeArt.objects.get_or_create(navn_dk='Torsk', skematype=skematype)
        produkttype, _ = ProduktType.objects.get_or_create(fiskeart=fiskeart)

        virksomhed, _ = Virksomhed.objects.get_or_create(cvr='12345678')

        if not Indberetning.objects.exists():
            for periode in (afgiftsperiode1, afgiftsperiode2):
                for i, indberetnings_type in enumerate(('indhandling', 'pelagisk', 'fartøj')):
                    if indberetnings_type == 'indhandling':
                        navn = 'Bygd for indhandling'
                    else:
                        navn = 'Tidligere fartøj'
                    indberetning = Indberetning.objects.create(skematype=skematype,
                                                               virksomhed=virksomhed,
                                                               afgiftsperiode=periode,
                                                               indberetnings_type=indberetnings_type,
                                                               indberetters_cpr='123456-1955')

                    IndberetningLinje.objects.create(indberetning=indberetning,
                                                     navn=navn,
                                                     salgsvægt=10,
                                                     levende_vægt=20,
                                                     salgspris=400,
                                                     produkttype=produkttype)

        try:
            BeregningsModel2021.objects.create(
                navn='TestBeregningsModel',
                transport_afgift_rate=Decimal(1),
            )
        except IntegrityError:
            beregningsmodel = BeregningsModel2021.objects.get(navn='TestBeregningsModel')
            beregningsmodel.transport_afgift_rate = Decimal(1)
            beregningsmodel.save()
