from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from administration.models import Afgiftsperiode, FiskeArt, FangstType, Ressource, ProduktKategori, BeregningsModel2021
from indberetning.models import Indberetning, Virksomhed, IndberetningLinje
from datetime import date
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample data only for development environments'

    def handle(self, *args, **options):
        if settings.DEBUG is False:
            print('DEBUG needs to be True (dev-environment)')
            return

        User = get_user_model()
        user, _ = User.objects.get_or_create(username='admin')
        user.set_password('admin')
        user.save()

        for fish, place in [
            ('Reje', 'Havgående'),
            ('Reje', 'Kystnært'),
            ('Hellefisk', 'Havgående'),
            ('Hellefisk', 'Kystnært'),
            ('Torsk', 'Havgående'),
            ('Krabbe', 'Havgående'),
            ('Kuller', 'Havgående'),
            ('Sej', 'Havgående'),
            ('Rødfisk', 'Havgående'),
            ('Kammusling', 'Havgående'),
            ('Makrel', 'Havgående'),
            ('Makrel', 'Kystnært'),
            ('Sild', 'Havgående'),
            ('Sild', 'Kystnært'),
            ('Lodde', 'Havgående'),
            ('Lodde', 'Kystnært'),
            ('Blåhvilling', 'Havgående'),
            ('Blåhvilling', 'Kystnært'),
            ('Guldlaks', 'Havgående'),
            ('Guldlaks', 'Kystnært'),
        ]:

            try:
                fiskeart = FiskeArt.objects.create(navn=fish)
            except IntegrityError:
                fiskeart = FiskeArt.objects.get(navn=fish)
            try:
                fangsttype = FangstType.objects.create(navn=place)
            except IntegrityError:
                fangsttype = FangstType.objects.get(navn=place)
            try:
                Ressource.objects.create(
                    fiskeart=fiskeart,
                    fangsttype=fangsttype,
                )
            except IntegrityError:
                pass

        kategorier = []
        for kategori in ('Hel fisk', 'Filet', 'Biprodukt'):
            kat, _ = ProduktKategori.objects.get_or_create(navn=kategori)
            kategorier.append(kat)

        afgiftsperiode1, _ = Afgiftsperiode.objects.get_or_create(navn='4. kvartal 2021', vis_i_indberetning=True, dato_fra=date(2021, 10, 1), dato_til=date(2021, 12, 31))

        afgiftsperiode2, _ = Afgiftsperiode.objects.get_or_create(navn='3. kvartal 2021', vis_i_indberetning=True, dato_fra=date(2021, 7, 1), dato_til=date(2021, 9, 30))

        kategorier = []
        for kategori in ('Hel fisk', 'Filet', 'Biprodukt'):
            kat, _ = ProduktKategori.objects.get_or_create(navn=kategori)
            kategorier.append(kat)

        virksomhed, _ = Virksomhed.objects.get_or_create(cvr='12345678')

        if not Indberetning.objects.exists():
            for periode in (afgiftsperiode1, afgiftsperiode2):
                for i, indberetnings_type in enumerate(('indhandling', 'pelagisk', 'fartøj')):
                    if indberetnings_type == 'indhandling':
                        navn = 'Bygd for indhandling'
                        kategori = None
                    else:
                        navn = 'Tidligere fartøj'
                        kategori = kategorier[i]
                    indberetning = Indberetning.objects.create(virksomhed=virksomhed,
                                                               afgiftsperiode=periode,
                                                               navn=navn,
                                                               indberetnings_type=indberetnings_type,
                                                               indberetters_cpr='123456-1955')

                    IndberetningLinje.objects.create(indberetning=indberetning,
                                                     salgsvægt=10,
                                                     levende_vægt=20,
                                                     salgspris=400,
                                                     kategori=kategori,
                                                     fiskeart=FiskeArt.objects.get(navn='Torsk'))

        try:
            BeregningsModel2021.objects.create(
                navn='TestBeregningsModel',
                transport_afgift_rate=Decimal(1),
            )
        except IntegrityError:
            beregningsmodel = BeregningsModel2021.objects.get(navn='TestBeregningsModel')
            beregningsmodel.transport_afgift_rate = Decimal(1)
            beregningsmodel.save()
