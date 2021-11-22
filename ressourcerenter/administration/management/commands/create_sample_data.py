from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from indberetning.models import Indberetning, Virksomhed, Kategori, IndberetningLinje
from administration.models import Afgiftsperiode, FiskeArt, Kvartal


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

        afgiftsperiode1, _ = Afgiftsperiode.objects.get_or_create(navn='4. kvartal 2021', vis_i_indberetning=True, aarkvartal=kvartal1)

        afgiftsperiode2, _ = Afgiftsperiode.objects.get_or_create(navn='3. kvartal 2021', vis_i_indberetning=True, aarkvartal=kvartal2)
        reje, _ = FiskeArt.objects.get_or_create(navn='reje')
        torsk, _ = FiskeArt.objects.get_or_create(navn='Torsk')
        Kategori.objects.get_or_create(navn='Hel fisk')
        Kategori.objects.get_or_create(navn='Filet')
        Kategori.objects.get_or_create(navn='Bi produkt')
        virksomhed, _ = Virksomhed.objects.get_or_create(cvr='12345678')

        if not Indberetning.objects.exists():
            for periode in (afgiftsperiode1, afgiftsperiode2):
                indberetning = Indberetning.objects.create(virksomhed=virksomhed,
                                                           afgiftsperiode=periode,
                                                           navn='Bygd for indhandling',
                                                           indberetnings_type='indhandling',
                                                           indberetters_cpr='123456-1955')

                IndberetningLinje.objects.create(indberetning=indberetning,
                                                 salgs_vægt=10,
                                                 levende_vægt=20,
                                                 salgs_pris=400,
                                                 fiskeart=torsk,
                                                 )
