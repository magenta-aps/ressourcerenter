from django.test import TestCase
from administration.models import Kvartal, Afgiftsperiode, SatsTabelElement, Ressource, Fangst, BeregningsModel2021
from decimal import Decimal


class AfgiftTestCase(TestCase):

    '''
    §4
    Test at havgående fiskeri efter
        rejer, hellefisk, torsk, krabber, kuller, sej, rødfisk og kammuslinger
    Test at kystnært fiskeri efter
        rejer og hellefisk
    beskattes iht. §§4-7
    '''

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        kvartal, created = Kvartal.objects.get_or_create(aar=2021, kvartal=3)
        kvartal, created = Kvartal.objects.get_or_create(aar=2021, kvartal=4)
        tabel, created = Afgiftsperiode.objects.get_or_create(aarkvartal=kvartal)

        cls.tabel = Afgiftsperiode.objects.get(aarkvartal=kvartal)

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
            SatsTabelElement.objects.create(
                tabel=tabel,
                ressource=Ressource.objects.get(fiskeart__navn=navn, fangsttype__navn=sted),
                rate_procent_indhandling=rate_procent_indhandling,
                rate_procent_export=rate_procent_export,
            )

        for navn, sted, rate_prkg_groenland, rate_prkg_udenlandsk in [
            ('Sild', 'Kystnært', 0.25, 0.80),
            ('Lodde', 'Kystnært', 0.15, 0.70),
            ('Makrel', 'Kystnært', 0.4, 1),
            ('Blåhvilling', 'Kystnært', 0.15, 0.70),
            ('Guldlaks', 'Kystnært', 0.15, 0.70),
        ]:
            SatsTabelElement.objects.create(
                tabel=tabel,
                ressource=Ressource.objects.get(fiskeart__navn=navn, fangsttype__navn=sted),
                rate_prkg_groenland=rate_prkg_groenland,
                rate_prkg_udenlandsk=rate_prkg_udenlandsk,
            )

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
        items = [
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=False
            )
        ]
        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.tabel, items)
        self.assertEquals(result[0].afgift, Decimal(55))

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
            tabel=self.tabel,
            ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
        )
        rate_element.rate_procent_export = 0
        rate_element.rate_procent_indhandling = 0
        rate_element.rate_pr_kg_export = Decimal(0.2)
        rate_element.rate_pr_kg_indhandling = Decimal(0.05)
        rate_element.save()
        items = [
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                overfoert_til_tredje_part=False,
                export_inkluderet_i_pris=False
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=False,
                overfoert_til_tredje_part=True,
                export_inkluderet_i_pris=False
            )
        ]
        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.tabel, items)
        self.assertEquals(result[0].afgift, Decimal(20))
        self.assertEquals(result[1].afgift, Decimal(20))

    def test_landed_calculation_2(self):
        '''
        §5.2
        Hvis der er indhandlet i Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) < 8 kr.pr.kg
        er grundafgift 0.05 kr.pr.kg
        '''
        rate_element = SatsTabelElement.objects.get(
            tabel=self.tabel,
            ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
        )
        rate_element.rate_procent_export = 0
        rate_element.rate_procent_indhandling = 0
        rate_element.rate_pr_kg_export = Decimal(0.2)
        rate_element.rate_pr_kg_indhandling = Decimal(0.05)
        rate_element.save()
        items = [
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=False,
                overfoert_til_tredje_part=False,
                export_inkluderet_i_pris=False
            )
        ]
        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.tabel, items)
        self.assertEquals(result[0].afgift, Decimal(5))

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
        items = [
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=False,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Torsk', fangsttype__navn='Havgående'),
                pris=Decimal('500.0'),
                vaegt=Decimal('100.0'),
                til_export=False,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Hellefisk', fangsttype__navn='Kystnært'),
                pris=Decimal('300.0'),
                vaegt=Decimal('150.0'),
                til_export=True,
            )
        ]
        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.tabel, items)
        self.assertEquals(3, len(result))
        self.assertEquals(Decimal(50), result[0].afgift)
        self.assertEquals(Decimal(25), result[1].afgift)
        self.assertEquals(Decimal(15), result[2].afgift)

    def test_transferred_calculation_3(self):
        '''
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og gnsn. salgspris for fiskearten i kvartal(nuv.kvartal - 6 mdr) >= 17 kr/kg
        er ressourcerenteafgift 5% + 1% pr kr i gnsn salgspris (rundet op, så 17,5 kr/kg = 6%, 18,5 kr/kg = 7%)
        Dog max 17,5%
        '''
        rate_element = SatsTabelElement.objects.get(
            tabel=self.tabel,
            ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
        )
        rate_element.rate_procent_export = Decimal(7)
        rate_element.save()
        items = [
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=False
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=False,
                overfoert_til_tredje_part=True,
                export_inkluderet_i_pris=False
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Reje', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=False,
                overfoert_til_tredje_part=False,
                export_inkluderet_i_pris=False
            )
        ]
        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.tabel, items)
        self.assertEquals(result[0].afgift, Decimal(77))
        self.assertEquals(result[1].afgift, Decimal(70))
        self.assertEquals(result[2].afgift, Decimal(50))

    def test_transferred_calculation_4(self):
        '''
        §7.4
        Hvis der er overdraget til tredjemand eller udført af Grønland
        og fiskearten er kammuslinger
        er ressourcerenteafgift 5%
        '''
        rate_element = SatsTabelElement.objects.get(
            tabel=self.tabel,
            ressource=Ressource.objects.get(fiskeart__navn='Kammusling', fangsttype__navn='Havgående'),
        )
        rate_element.rate_procent_export = Decimal(5)
        rate_element.save()
        items = [
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Kammusling', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=False
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Kammusling', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Kammusling', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=False,
                overfoert_til_tredje_part=True,
                export_inkluderet_i_pris=False
            ),
        ]
        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.tabel, items)
        self.assertEquals(result[0].afgift, Decimal(55))
        self.assertEquals(result[1].afgift, Decimal(50))
        self.assertEquals(result[2].afgift, Decimal(50))

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
        items = [
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Sild', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Sild', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=False,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Lodde', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Lodde', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=False,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Makrel', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Makrel', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=False,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Blåhvilling', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Blåhvilling', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=False,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Guldlaks', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Guldlaks', fangsttype__navn='Kystnært'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=False,
            ),
        ]

        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.tabel, items)
        self.assertEquals(result[0].afgift, Decimal(25))
        self.assertEquals(result[1].afgift, Decimal(80))
        self.assertEquals(result[2].afgift, Decimal(15))
        self.assertEquals(result[3].afgift, Decimal(70))
        self.assertEquals(result[4].afgift, Decimal(40))
        self.assertEquals(result[5].afgift, Decimal(100))
        self.assertEquals(result[6].afgift, Decimal(15))
        self.assertEquals(result[7].afgift, Decimal(70))
        self.assertEquals(result[8].afgift, Decimal(15))
        self.assertEquals(result[9].afgift, Decimal(70))

    def test_invalid_catch(self):
        items = [
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Sild', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Lodde', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Makrel', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Blåhvilling', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
            Fangst.objects.create(
                ressource=Ressource.objects.get(fiskeart__navn='Guldlaks', fangsttype__navn='Havgående'),
                pris=Decimal('1000.0'),
                vaegt=Decimal('100.0'),
                til_export=True,
                export_inkluderet_i_pris=True,
                overfoert_til_tredje_part=True,
                fartoej_groenlandsk=True,
            ),
        ]

        model = BeregningsModel2021.objects.create()
        result = model.calculate(self.tabel, items)
        self.assertEquals(result[0].rate_element, None)
        self.assertEquals(result[1].rate_element, None)
        self.assertEquals(result[2].rate_element, None)
        self.assertEquals(result[3].rate_element, None)
        self.assertEquals(result[4].rate_element, None)
