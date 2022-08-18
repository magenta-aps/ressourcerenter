from django.template.defaultfilters import register


@register.filter
def split(text, filter):
    return text.split(filter)
