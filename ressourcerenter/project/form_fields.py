from django import forms
from django.forms.widgets import TextInput


class LocalizedDecimalField(forms.DecimalField):
    def __init__(self, max_value=None, min_value=None, max_digits=None, decimal_places=None, **kwargs):
        kwargs['widget'] = TextInput  # use text input to avoid input type=number
        kwargs['localize'] = True  # allow localized values such as 1.200,24
        super(LocalizedDecimalField, self).__init__(max_value=max_value,
                                                    min_value=min_value,
                                                    max_digits=max_digits,
                                                    decimal_places=decimal_places,
                                                    **kwargs)


class DateInput(forms.DateInput):
    input_type = 'date'
