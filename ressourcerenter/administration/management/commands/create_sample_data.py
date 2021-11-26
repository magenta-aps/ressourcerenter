from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from administration.models import Afgiftsperiode, FiskeArt, Kvartal
from indberetning.models import Indberetning, Virksomhed, ProduktKategori, IndberetningLinje


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

        kvartal1, _ = Kvartal.objects.get_or_create(aar=2021, kvartal=4)
        kvartal2, _ = Kvartal.objects.get_or_create(aar=2021, kvartal=3)

        afgiftsperiode1, _ = Afgiftsperiode.objects.get_or_create(navn='4. kvartal 2021',
                                                                  vis_i_indberetning=True,
                                                                  aarkvartal=kvartal1)
        afgiftsperiode2, _ = Afgiftsperiode.objects.get_or_create(navn='3. kvartal 2021',
                                                                  vis_i_indberetning=True,
                                                                  aarkvartal=kvartal2)
        kategorier = []
        for kategori in ('Hel fisk', 'Filet', 'Biprodukt'):
            kat, _ = ProduktKategori.objects.get_or_create(navn=kategori)
            kategorier.append(kat)

        reje, _ = FiskeArt.objects.get_or_create(navn='reje')
        torsk, _ = FiskeArt.objects.get_or_create(navn='Torsk')
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
