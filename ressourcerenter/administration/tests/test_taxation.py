from django.test import TransactionTestCase
from administration.models import Afgiftsperiode, SatsTabelElement, Ressource, BeregningsModel2021, FiskeArt, FangstType
from indberetning.models import Virksomhed, Indberetning, IndberetningLinje
from decimal import Decimal
from datetime import date


class AfgiftTestCase(TransactionTestCase):

    '''
    §4
    Test at havgående fiskeri efter
        rejer, hellefisk, torsk, krabber, kuller, sej, rødfisk og kammuslinger
    Test at kystnært fiskeri efter
        rejer og hellefisk
    beskattes iht. §§4-7
    '''

    def setUp(self):
        super().setUpClass()

        self.periode, created = Afgiftsperiode.objects.get_or_create(
            navn='4. Kvartal 2021',
            dato_fra=date(year=2021, month=10, day=1),
            dato_til=date(year=2021, month=12, day=31)
        )

        for navn, sted, rate_procent_indhandling, rate_procent_export in [
            ('Reje', 'Havgående', 5, 5),
            ('Hellefisk', 'Havgående', 5, 5),
            ('Torsk', 'Havgående', 5, 5),
            ('Krabbe', 'Havgående', 5, 5),
            ('Kuller', 'Havgående', 5, 5),
            ('Sej', 'Havgående', 5, 5),
            ('Rødfisk', 'Havgående', 5, 5),
            ('Kammusling', 'Havgående', 5, 5),
            ('Reje', 'Kystnært', 5, 5),
            ('Hellefisk', 'Kystnært', 5, 5),
        ]:
            fiskeart, _ = FiskeArt.objects.get_or_create(navn=navn)
            fangsttype, _ = FangstType.objects.get_or_create(navn=sted)
            ressource, _ = Ressource.objects.get_or_create(fiskeart=fiskeart, fangsttype=fangsttype)
            SatsTabelElement.objects.get_or_create(
                periode=self.periode,
                ressource=ressource,
                defaults={
                    'rate_procent_indhandling': rate_procent_indhandling,
                    'rate_procent_export': rate_procent_export,
                }
            )

        for navn, sted, rate_prkg_groenland, rate_prkg_udenlandsk in [
            ('Sild', 'Kystnært', 0.25, 0.80),
            ('Lodde', 'Kystnært', 0.15, 0.70),
            ('Makrel', 'Kystnært', 0.4, 1),
            ('Blåhvilling', 'Kystnært', 0.15, 0.70),
            ('Guldlaks', 'Kystnært', 0.15, 0.70),
        ]:
            fiskeart, _ = FiskeArt.objects.get_or_create(navn=navn)
            fangsttype, _ = FangstType.objects.get_or_create(navn=sted)
            ressource, _ = Ressource.objects.get_or_create(fiskeart=fiskeart, fangsttype=fangsttype)
            SatsTabelElement.objects.get_or_create(
                periode=self.periode,
                ressource=ressource,
                defaults={
                    'rate_prkg_groenland': rate_prkg_groenland,
                    'rate_prkg_udenlandsk': rate_prkg_udenlandsk,
                }
            )

        self.virksomhed = Virksomhed.objects.create(cvr=1234)

    def _calculate(self, indberetnings_type='havgående', fiskeart=None, salgspris=0, levende_vaegt=0, salgsvaegt=0, til_export=False, overfoert_til_tredje_part=False, export_inkluderet_i_pris=False, fartoej_groenlandsk=True):
        indberetning = Indberetning.objects.create(
            afgiftsperiode=self.periode,
            virksomhed=self.virksomhed,
            indberetnings_type=indberetnings_type
        )
        IndberetningLinje.objects.create(
            indberetning=indberetning,
            fiskeart=FiskeArt.objects.get(navn=fiskeart),
            salgspris=Decimal(salgspris),
            levende_vægt=Decimal(levende_vaegt),
            salgsvægt=Decimal(salgsvaegt),
        )
        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.periode, indberetning, til_export=til_export, overfoert_til_tredje_part=overfoert_til_tredje_part, export_inkluderet_i_pris=export_inkluderet_i_pris, fartoej_groenlandsk=fartoej_groenlandsk)
        return result[0]

    def test_transport_addition_forminput(self):
        '''
        §4.2
        Test at der kan markeres om prisen er inklusive transport ud af Grønland
        I modsat fald forøges salgsprisen med 1 kr. pr .kg.
        (f.eks. om der er en checkbox, og at form submission giver opdaterede data)
        '''
        pass

    def test_transport_addition_calculation(self):
        '''
        Test at den forøgede salgspris passer med oprindelig salgspris + 1*vægt
        Gælder for samme type fiskeri som ovenfor
        '''
        result = self._calculate(fiskeart='Reje', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=False)
        self.assertEquals(result.afgift, Decimal(55))

    def test_admin_update_price(self):
        '''
        §4.3
        Test at skatteforvaltningen kan overstyre salgsprisen
        (f.eks. at der er et felt til det, og at form submission giver opdaterede data)
        '''
        pass

    def test_transferred_forminput(self):
        '''
        §5
        Test at der kan angives om fangsten er overdraget til tredjemand eller udført af Grønland
        (f.eks. om der er en checkbox, og at form submission giver opdaterede data)
        '''
        pass

    def test_transferred_calculation_1(self):
        '''
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) < 12 kr/kg
        er grundafgift 0.20 kr.pr.kg
        '''
        rate_element = SatsTabelElement.objects.get(
            periode=self.periode,
            ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
        )
        rate_element.rate_procent_export = 0
        rate_element.rate_procent_indhandling = 0
        rate_element.rate_pr_kg_export = Decimal(0.2)
        rate_element.rate_pr_kg_indhandling = Decimal(0.05)
        rate_element.save()

        result = self._calculate(fiskeart='Reje', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=False)
        self.assertEquals(result.afgift, Decimal(20))

        result = self._calculate(fiskeart='Reje', salgspris=1000, levende_vaegt=100, salgsvaegt=100, overfoert_til_tredje_part=True)
        self.assertEquals(result.afgift, Decimal(20))

    def test_landed_calculation_2(self):
        '''
        §5.2
        Hvis der er indhandlet i Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) < 8 kr.pr.kg
        er grundafgift 0.05 kr.pr.kg
        '''
        rate_element = SatsTabelElement.objects.get(
            periode=self.periode,
            ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
        )
        rate_element.rate_procent_export = 0
        rate_element.rate_procent_indhandling = 0
        rate_element.rate_pr_kg_export = Decimal(0.2)
        rate_element.rate_pr_kg_indhandling = Decimal(0.05)
        rate_element.save()

        result = self._calculate(fiskeart='Reje', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=False, overfoert_til_tredje_part=False, export_inkluderet_i_pris=False)
        self.assertEquals(result.afgift, Decimal(5))

    def test_transferred_calculation_2(self):
        '''
        §6
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) >= 12 kr/kg og < 17 kr/kg
        er ressourcerenteafgift 5% af prisen
        §7
        Ved indhandling
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) >= 8 kr/kg
        er ressourcerenteafgift 5% af prisen
        '''
        result = self._calculate(fiskeart='Reje', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=False)
        self.assertEquals(Decimal(50), result.afgift)

        result = self._calculate(fiskeart='Torsk', salgspris=500, levende_vaegt=100, salgsvaegt=100, til_export=False)
        self.assertEquals(Decimal(25), result.afgift)

        result = self._calculate(fiskeart='Hellefisk', indberetnings_type='indhandling', salgspris=300, levende_vaegt=150, salgsvaegt=150, til_export=True, export_inkluderet_i_pris=True)
        self.assertEquals(Decimal(15), result.afgift)

    def test_transferred_calculation_3(self):
        '''
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) >= 17 kr/kg
        er ressourcerenteafgift 5% + 1% pr kr i gnsn salgspris (rundet op, så 17,5 kr/kg = 6%, 18,5 kr/kg = 7%)
        Dog max 17,5%
        '''
        rate_element = SatsTabelElement.objects.get(
            periode=self.periode,
            ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
        )
        rate_element.rate_procent_export = Decimal(7)
        rate_element.save()

        result = self._calculate(fiskeart='Reje', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=False)
        self.assertEquals(result.afgift, Decimal(77))

        result = self._calculate(fiskeart='Reje', salgspris=1000, levende_vaegt=100, salgsvaegt=100, overfoert_til_tredje_part=True)
        self.assertEquals(result.afgift, Decimal(70))

        result = self._calculate(fiskeart='Reje', salgspris=1000, levende_vaegt=100, salgsvaegt=100)
        self.assertEquals(result.afgift, Decimal(50))

    def test_transferred_calculation_4(self):
        '''
        §7.4
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og fiskearten er kammuslinger
        er ressourcerenteafgift 5%
        '''
        rate_element = SatsTabelElement.objects.get(
            periode=self.periode,
            ressource=Ressource.objects.get(fiskeart__navn='Kammusling', fangsttype__navn='Havgående'),
        )
        rate_element.rate_procent_export = Decimal(5)
        rate_element.save()

        result = self._calculate(fiskeart='Kammusling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=False)
        self.assertEquals(result.afgift, Decimal(55))

        result = self._calculate(fiskeart='Kammusling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True)
        self.assertEquals(result.afgift, Decimal(50))

        result = self._calculate(fiskeart='Kammusling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=False, export_inkluderet_i_pris=False, overfoert_til_tredje_part=True)
        self.assertEquals(result.afgift, Decimal(50))

    def test_pelagic(self):
        '''
        §8
        Pelagisk fiskeri - afgifter for fartøj fra
                Grønland | Andre
        Sild        0,25 | 0,80
        Lodde       0,15 | 0,70
        Makrel      0,40 | 1,00
        Blåhvilling 0,15 | 0,70
        Guldlaks    0,15 | 0,70
        kr.pr.kg levende vægt
        '''
        result = self._calculate(fiskeart='Sild', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True)
        self.assertEquals(result.afgift, Decimal(25))

        result = self._calculate(fiskeart='Sild', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True, fartoej_groenlandsk=False)
        self.assertEquals(result.afgift, Decimal(80))

        result = self._calculate(fiskeart='Lodde', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True)
        self.assertEquals(result.afgift, Decimal(15))

        result = self._calculate(fiskeart='Lodde', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True, fartoej_groenlandsk=False)
        self.assertEquals(result.afgift, Decimal(70))

        result = self._calculate(fiskeart='Makrel', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True)
        self.assertEquals(result.afgift, Decimal(40))

        result = self._calculate(fiskeart='Makrel', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True, fartoej_groenlandsk=False)
        self.assertEquals(result.afgift, Decimal(100))

        result = self._calculate(fiskeart='Blåhvilling', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True)
        self.assertEquals(result.afgift, Decimal(15))

        result = self._calculate(fiskeart='Blåhvilling', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True, fartoej_groenlandsk=False)
        self.assertEquals(result.afgift, Decimal(70))

        result = self._calculate(fiskeart='Guldlaks', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True, fartoej_groenlandsk=True)
        self.assertEquals(result.afgift, Decimal(15))

        result = self._calculate(fiskeart='Guldlaks', indberetnings_type='indhandling', salgspris=1000, levende_vaegt=100, salgsvaegt=100, til_export=True, export_inkluderet_i_pris=True, overfoert_til_tredje_part=True, fartoej_groenlandsk=False)
        self.assertEquals(result.afgift, Decimal(70))
