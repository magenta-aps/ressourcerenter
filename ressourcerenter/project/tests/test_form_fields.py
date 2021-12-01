from decimal import Decimal

from django.test import TestCase
from django.utils import translation
from django.utils.formats import get_format

from project.form_fields import LocalizedDecimalField


class TestLocalizedDecimalField(TestCase):

    @translation.override('da-DK')
    def test_danish(self):
        self.assertEqual('da-dk', translation.get_language())
        self.assertEqual(get_format('DECIMAL_SEPARATOR'), ',')
        self.assertEqual(get_format('THOUSAND_SEPARATOR'), '.')
        field = LocalizedDecimalField()
        self.assertEqual(field.clean('1.200,25'), Decimal('1200.25'))

    @translation.override('kl')
    def test_greenlandic(self):
        """
        kl is not a language and therefore not a locale.
        We want to combine a none existing locale (kl) with the danish number formatting.
        Overridning the formatting (https://docs.djangoproject.com/en/3.2/topics/i18n/formatting/#creating-custom-format-files)
        wont work since django dose not recognize the kl as a language,
        so it defaults to "english number formatting" unless we set the following settings in setting.py
        to force default to dk number formatting
        # DECIMAL_SEPARATOR = ","
        # THOUSAND_SEPARATOR = '.'
        """
        self.assertEqual('kl', translation.get_language())
        field = LocalizedDecimalField()
        self.assertEqual(get_format('DECIMAL_SEPARATOR'), ',')
        self.assertEqual(get_format('THOUSAND_SEPARATOR'), '.')
        self.assertEqual(field.clean('1.200,25'), Decimal('1200.25'))

    @translation.override('en')
    def test_english(self):
        self.assertEqual('en', translation.get_language())
        field = LocalizedDecimalField()
        self.assertEqual(get_format('DECIMAL_SEPARATOR'), '.')
        self.assertEqual(get_format('THOUSAND_SEPARATOR'), ',')
        self.assertEqual(field.clean('1,200.25'), Decimal('1200.25'))
